from datetime import datetime
from dateutil import tz
from django.conf import settings
from ratelimit.utils import is_ratelimited
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Template, RequestContext
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import smart_str
from django.db.models import F
from django.urls import reverse_lazy, reverse
from pathlib import Path
import json
import os
import re

from .models import Puzzle, Hunt, Submission, Message, Unlockable, Prepuzzle, Hint
from .forms import AnswerForm, HintRequestForm

import logging
logger = logging.getLogger(__name__)

DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def protected_static(request, file_path):
    """
    A view to serve protected static content. Does a permission check and if it passes,
    the file is served via X-Sendfile.
    """

    allowed = False
    path = Path(file_path)
    base = path.parts[0]
    response = HttpResponse()
    if(len(path.parts) < 2):
        return HttpResponseNotFound('<h1>Page not found</h1>')

    if(base == "puzzles" or base == "solutions"):
        puzzle_id = re.match(r'[0-9a-fA-F]+', path.parts[1])
        if(puzzle_id is None):
            return HttpResponseNotFound('<h1>Page not found</h1>')

        puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id.group(0))
        hunt = puzzle.hunt
        user = request.user
        disposition = 'filename="{}_{}"'.format(puzzle.safename, path.name)
        response['Content-Disposition'] = disposition
        if (hunt.is_public or user.is_staff):
            allowed = True
        elif(base == "puzzles"):  # This is messy and the most common case, this should be fixed
            team = hunt.team_from_user(user)
            if (team is not None and puzzle in team.unlocked.all()):
                allowed = True
    else:
        allowed = True

    if allowed:
        # let apache determine the correct content type
        response['Content-Type'] = ""
        # This is what lets django access the normally restricted /media/
        response['X-Sendfile'] = smart_str(os.path.join(settings.MEDIA_ROOT, file_path))
        return response
    else:
        logger.info("User %s tried to access %s and failed." % (str(request.user), file_path))

    return HttpResponseNotFound('<h1>Page not found</h1>')


def hunt(request, hunt_num):
    """
    The main view to render hunt templates. Does various permission checks to determine the set
    of puzzles to display and then renders the string in the hunt's "template" field to HTML.
    """

    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    team = hunt.team_from_user(request.user)

    # Admins get all access, wrong teams/early lookers get an error page
    # real teams get appropriate puzzles, and puzzles from past hunts are public
    if (hunt.is_public or request.user.is_staff):
        puzzle_list = hunt.puzzle_set.all()

    elif(team and team.is_playtester_team and team.playtest_started):
        puzzle_list = team.unlocked.filter(hunt=hunt)

    # Hunt has not yet started
    elif(hunt.is_locked):
        if(hunt.is_day_of_hunt):
            return render(request, 'access_error.html', {'reason': "hunt"})
        else:
            return hunt_prepuzzle(request, hunt_num)

    # Hunt has started
    elif(hunt.is_open):
        # see if the team does not belong to the hunt being accessed
        if (not request.user.is_authenticated):
            return redirect('%s?next=%s' % (reverse_lazy(settings.LOGIN_URL), request.path))

        elif(team is None or (team.hunt != hunt)):
            return render(request, 'access_error.html', {'reason': "team"})
        else:
            puzzle_list = team.unlocked.filter(hunt=hunt)

        # No else case, all 3 possible hunt states have been checked.

    puzzles = sorted(puzzle_list, key=lambda p: p.puzzle_number)
    if(team is None):
        solved = []
    else:
        solved = team.solved.all()
    context = {'hunt': hunt, 'puzzles': puzzles, 'team': team, 'solved': solved}

    return HttpResponse(Template(hunt.template).render(RequestContext(request, context)))


def current_hunt(request):
    """ A simple view that calls ``huntserver.hunt_views.hunt`` with the current hunt's number. """
    return hunt(request, Hunt.objects.get(is_current_hunt=True).hunt_number)


def prepuzzle(request, prepuzzle_num):
    """
    A view to handle answer submissions via POST and render the prepuzzle's template.
    """

    puzzle = Prepuzzle.objects.get(pk=prepuzzle_num)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = re.sub(r"[ _\-;:+,.!?]", "", form.cleaned_data['answer'])

            # Compare against correct answer
            if(puzzle.answer.lower() == user_answer.lower()):
                is_correct = True
                response = puzzle.response_string
                logger.info("User %s solved prepuzzle %s." % (str(request.user), prepuzzle_num))
            else:
                is_correct = False
                response = ""
        else:
            is_correct = None
            response = ""
        response_vars = {'response': response, 'is_correct': is_correct}
        return HttpResponse(json.dumps(response_vars))

    else:
        if(not (puzzle.released or request.user.is_staff)):
            return redirect('huntserver:current_hunt_info')
        form = AnswerForm()
        context = {'form': form, 'puzzle': puzzle}
        return HttpResponse(Template(puzzle.template).render(RequestContext(request, context)))


def hunt_prepuzzle(request, hunt_num):
    """
    A simple view that locates the correct prepuzzle for a hunt and redirects there if it exists.
    """
    curr_hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    if(hasattr(curr_hunt, "prepuzzle")):
        return prepuzzle(request, curr_hunt.prepuzzle.pk)
    else:
        # Maybe we can do something better, but for now, redirect to the main page
        return redirect('huntserver:current_hunt_info')


def current_prepuzzle(request):
    """
    A simple view that locates the correct prepuzzle for the current hunt and redirects to there.
    """
    return hunt_prepuzzle(request, Hunt.objects.get(is_current_hunt=True).hunt_number)


def get_ratelimit_key(group, request):
    return request.ratelimit_key


def puzzle_view(request, puzzle_id):
    """
    A view to handle answer submissions via POST, handle response update requests via AJAX, and
    render the basic per-puzzle pages.
    """
    puzzle = get_object_or_404(Puzzle, puzzle_id__iexact=puzzle_id)
    team = puzzle.hunt.team_from_user(request.user)

    if(team is not None):
        request.ratelimit_key = team.team_name

        is_ratelimited(request, fn=puzzle_view, key='user', rate='2/10s', method='POST',
                       increment=True)
    if(not puzzle.hunt.is_public):
        is_ratelimited(request, fn=puzzle_view, key=get_ratelimit_key, rate='5/m', method='POST',
                       increment=True)

    if(getattr(request, 'limited', False)):
        logger.info("User %s rate-limited for puzzle %s" % (str(request.user), puzzle_id))
        return HttpResponseForbidden()

    # Dealing with answer submissions, proper procedure is to create a submission
    # object and then rely on Submission.respond for automatic responses.
    if request.method == 'POST':
        if(team is None):
            if(puzzle.hunt.is_public):
                team = puzzle.hunt.dummy_team
            else:
                # If the hunt isn't public and you aren't signed in, please stop...
                return HttpResponse('fail')

        form = AnswerForm(request.POST)
        form.helper.form_action = reverse('huntserver:puzzle', kwargs={'puzzle_id': puzzle_id})

        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            s = Submission.objects.create(submission_text=user_answer, team=team,
                                          puzzle=puzzle, submission_time=timezone.now())
            s.respond()
        else:
            s = None

        # Deal with answers for public hunts
        if(puzzle.hunt.is_public):
            if(s is None):
                response = "Invalid Submission"
                is_correct = None
            else:
                response = s.response_text
                is_correct = s.is_correct

            context = {'form': form, 'puzzle': puzzle, 'PROTECTED_URL': settings.PROTECTED_URL,
                       'response': response, 'is_correct': is_correct}
            return render(request, 'puzzle.html', context)

        if(s is None):
            return HttpResponseBadRequest(form.errors.as_json())

        # Render response to HTML for live hunts
        submission_list = [render_to_string('puzzle_sub_row.html', {'submission': s})]

        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime(DT_FORMAT)
        except Submission.DoesNotExist:
            last_date = timezone.now().strftime(DT_FORMAT)

        # Send back rendered response for display
        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))

    # Will return HTML rows for all submissions the user does not yet have
    elif request.is_ajax():
        if(team is None):
            return HttpResponseNotFound('access denied')

        # Find which objects the user hasn't seen yet and render them to HTML
        last_date = datetime.strptime(request.GET.get("last_date"), DT_FORMAT)
        last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
        submissions = Submission.objects.filter(modified_date__gt=last_date)
        submissions = submissions.filter(team=team, puzzle=puzzle)
        submission_list = [render_to_string('puzzle_sub_row.html', {'submission': submission})
                           for submission in submissions]

        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime(DT_FORMAT)
        except Submission.DoesNotExist:
            last_date = timezone.now().strftime(DT_FORMAT)

        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))

    else:
        # Only allowed access if the hunt is public or if unlocked by team
        if(not puzzle.hunt.is_public):
            if(not request.user.is_authenticated):
                return redirect('%s?next=%s' % (reverse_lazy(settings.LOGIN_URL), request.path))

            if (not request.user.is_staff):
                if(team is None or puzzle not in team.unlocked.all()):
                    return render(request, 'access_error.html', {'reason': "puzzle"})

        # The logic above is negated to weed out edge cases, so here is a summary:
        # If we've made it here, the hunt is public OR the user is staff OR
        # the user 1) is signed in, 2) not staff, 3) is on a team, and 4) has access
        if(team is not None):
            submissions = puzzle.submission_set.filter(team=team).order_by('pk')
            disable_form = puzzle in team.solved.all()
        else:
            submissions = None
            disable_form = False
        form = AnswerForm(disable_form=disable_form)
        form.helper.form_action = reverse('huntserver:puzzle', kwargs={'puzzle_id': puzzle_id})
        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime(DT_FORMAT)
        except Submission.DoesNotExist:
            last_date = timezone.now().strftime(DT_FORMAT)
        context = {'form': form, 'submission_list': submissions, 'puzzle': puzzle,
                   'PROTECTED_URL': settings.PROTECTED_URL, 'last_date': last_date, 'team': team}
        return render(request, 'puzzle.html', context)


@login_required
def puzzle_hint(request, puzzle_id):
    """
    A view to handle hint requests via POST, handle response update requests via AJAX, and
    render the basic puzzle-hint pages.
    """
    puzzle = get_object_or_404(Puzzle, puzzle_id__iexact=puzzle_id)
    team = puzzle.hunt.team_from_user(request.user)
    if(team is None):
        return render(request, 'access_error.html', {'reason': "team"})

    if request.method == 'POST':
        # Can't request a hint if there aren't any left
        if(team.num_available_hints <= 0):
            return HttpResponseForbidden()

        form = HintRequestForm(request.POST)
        if form.is_valid():
            h = Hint.objects.create(request=form.cleaned_data['request'], puzzle=puzzle, team=team,
                                    request_time=timezone.now(), last_modified_time=timezone.now())
            team.num_available_hints = F('num_available_hints') - 1
            team.save()
            team.refresh_from_db()
        # Render response to HTML
        hint_list = [render_to_string('hint_row.html', {'hint': h})]

        try:
            last_hint = Hint.objects.latest('last_modified_time')
            last_date = last_hint.last_modified_time.strftime(DT_FORMAT)
        except Hint.DoesNotExist:
            last_date = timezone.now().strftime(DT_FORMAT)

        # Send back rendered response for display
        context = {'hint_list': hint_list, 'last_date': last_date,
                   'num_available_hints': team.num_available_hints}
        return HttpResponse(json.dumps(context))

    # Will return HTML rows for all submissions the user does not yet have
    elif request.is_ajax():

        # Find which objects the user hasn't seen yet and render them to HTML
        last_date = datetime.strptime(request.GET.get("last_date"), DT_FORMAT)
        last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
        hints = Hint.objects.filter(last_modified_time__gt=last_date)
        hints = hints.filter(team=team, puzzle=puzzle)
        hint_list = [render_to_string('hint_row.html', {'hint': hint}) for hint in hints]

        try:
            last_hint = Hint.objects.latest('last_modified_time')
            last_date = last_hint.last_modified_time.strftime(DT_FORMAT)
        except Hint.DoesNotExist:
            last_date = timezone.now().strftime(DT_FORMAT)

        context = {'hint_list': hint_list, 'last_date': last_date,
                   'num_available_hints': team.num_available_hints}
        return HttpResponse(json.dumps(context))

    else:
        if(puzzle not in team.unlocked.all()):
            return render(request, 'access_error.html', {'reason': "puzzle"})

        form = HintRequestForm()
        hints = team.hint_set.filter(puzzle=puzzle).order_by('pk')
        try:
            last_hint = Hint.objects.latest('last_modified_time')
            last_date = last_hint.last_modified_time.strftime(DT_FORMAT)
        except Hint.DoesNotExist:
            last_date = timezone.now().strftime(DT_FORMAT)
        context = {'form': form, 'puzzle': puzzle, 'hint_list': hints, 'last_date': last_date,
                   'team': team}
        return render(request, 'puzzle_hint.html', context)


@login_required
def chat(request):
    """
    A view to handle message submissions via POST, handle message update requests via AJAX, and
    render the hunt participant view of the chat.
    """
    team = Hunt.objects.get(is_current_hunt=True).team_from_user(request.user)
    if request.method == 'POST':
        # There is data in the post request, but we don't need anything but
        #   the message because normal users can't send as staff or other teams
        m = Message.objects.create(time=timezone.now(), text=request.POST.get('message'),
                                   is_response=False, team=team)
        team.num_waiting_messages = 0
        messages = [m]
    else:
        if(team is None):
            return render(request, 'access_error.html', {'reason': "team"})
        if(team.hunt.is_locked and not team.is_playtester_team):
            return render(request, 'access_error.html', {'reason': "hunt"})
        if request.is_ajax():
            messages = Message.objects.filter(pk__gt=request.GET.get("last_pk"))
        else:
            messages = Message.objects
        messages = messages.filter(team=team).order_by('time')

    # The whole message_dict format is for ajax/template uniformity
    rendered_messages = render_to_string('chat_messages.html',
                                         {'messages': messages, 'team_name': team.team_name})
    message_dict = {team.team_name: {'pk': team.pk, 'messages': rendered_messages}}
    try:
        last_pk = Message.objects.latest('id').id
    except Message.DoesNotExist:
        last_pk = 0
    team.num_waiting_messages = 0

    team.save()  # Save last_*_message vars
    context = {'message_dict': message_dict, 'last_pk': last_pk}
    if request.is_ajax() or request.method == 'POST':
        return HttpResponse(json.dumps(context))
    else:
        context['team'] = team
        return render(request, 'chat.html', context)


@login_required
def chat_status(request):
    """
    A view ajax requests for the status of waiting chat messages for a team.
    """
    team = Hunt.objects.get(is_current_hunt=True).team_from_user(request.user)
    if request.method == 'GET' and request.is_ajax():
        if(team is None):
            return render(request, 'access_error.html', {'reason': "team"})
        status = team.num_waiting_messages
        return HttpResponse(json.dumps({"num_messages": status}))
    else:
        return HttpResponseNotFound()


@login_required
def unlockables(request):
    """ A view to render the unlockables page for hunt participants. """
    team = Hunt.objects.get(is_current_hunt=True).team_from_user(request.user)
    if(team is None):
        return render(request, 'access_error.html', {'reason': "team"})
    unlockables = Unlockable.objects.filter(puzzle__in=team.solved.all())
    return render(request, 'unlockables.html', {'unlockables': unlockables, 'team': team})
