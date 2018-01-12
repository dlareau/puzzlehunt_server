from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.template import Template, RequestContext
from django.utils.encoding import smart_str
from datetime import datetime
from dateutil import tz
import json
import os

from .models import Puzzle, Hunt, Submission, Message, Team, Unlockable
from .forms import AnswerForm
from .utils import respond_to_submission, team_from_user_hunt, dummy_team_from_hunt


@login_required
def protected_static(request, file_path):
    """
    A view to serve protected static content. Does a permission check and if it passes,
    the file is served via X-Sendfile.
    """

    allowed = False
    levels = file_path.split("/")
    if(levels[0] == "puzzles"):
        puzzle_id = levels[1][0:3]
        puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
        team = team_from_user_hunt(request.user, puzzle.hunt)
        # Only allowed access to the image if the puzzle is unlocked
        if (puzzle.hunt.is_public or request.user.is_staff or
           (team is not None and puzzle in team.unlocked.all())):
            allowed = True
    else:
        allowed = True

    if allowed:
        #if(settings.DEBUG):
        #    return redirect(settings.MEDIA_URL + file_path)
        response = HttpResponse()
        # let apache determine the correct content type
        response['Content-Type'] = ""
        # This is what lets django access the normally restricted /media/
        response['X-Sendfile'] = smart_str(os.path.join(settings.MEDIA_ROOT, file_path))
        return response

    return HttpResponseNotFound('<h1>Page not found</h1>')


@login_required
def hunt(request, hunt_num):
    """
    The main view to render hunt templates. Does various permission checks to determine the set
    of puzzles to display and then renders the string in the hunt's "template" field to HTML.
    """

    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    team = team_from_user_hunt(request.user, hunt)

    # Admins get all access, wrong teams/early lookers get an error page
    # real teams get appropriate puzzles, and puzzles from past hunts are public
    if(request.user.is_staff):
        puzzle_list = hunt.puzzle_set.all()

    elif(team and team.is_playtester_team):
        puzzle_list = team.unlocked.filter(hunt=hunt)

    # Hunt has not yet started
    elif(hunt.is_locked):
        return render(request, 'not_released.html', {'reason': "locked"})

    # Hunt has started
    elif(hunt.is_open):
        # see if the team does not belong to the hunt being accessed
        if(team is not None or (team.hunt != hunt)):
            return render(request, 'not_released.html', {'reason': "team"})
        else:
            puzzle_list = team.unlocked.filter(hunt=hunt)
    # Hunt is over
    elif(hunt.is_public):
        puzzle_list = hunt.puzzle_set.all()
    # How did you get here?
    else:
        return render(request, 'access_error.html')

    puzzles = sorted(puzzle_list, key=lambda p: p.puzzle_number)
    if(team is not None):
        solved = []
    else:
        solved = team.solved.all()
    context = {'hunt': hunt, 'puzzles': puzzles, 'team': team, 'solved': solved}

    return HttpResponse(Template(hunt.template).render(RequestContext(request, context)))


@login_required
def current_hunt(request):
    """ A simple view that calls ``huntserver.hunt_views.hunt`` with the current hunt's number. """
    return hunt(request, Hunt.objects.get(is_current_hunt=True).hunt_number)


@login_required
def puzzle_view(request, puzzle_id):
    """
    A view to handle answer submissions via POST, handle response update requests via AJAX, and
    render the basic per-puzzle pages.
    """

    puzzle = get_object_or_404(Puzzle, puzzle_id__iexact=puzzle_id)
    team = team_from_user_hunt(request.user, puzzle.hunt)

    # Dealing with answer submissions, proper procedure is to create a submission
    # object and then rely on utils.respond_to_submission for automatic responses.
    if request.method == 'POST':
        # Deal with answers from archived hunts
        if(puzzle.hunt.is_public):
            form = AnswerForm(request.POST)
            team = dummy_team_from_hunt(puzzle.hunt)
            if form.is_valid():
                user_answer = form.cleaned_data['answer']
                s = Submission.objects.create(submission_text=user_answer,
                    puzzle=puzzle, submission_time=timezone.now(), team=team)
                response = respond_to_submission(s)
                is_correct = s.is_correct
            else:
                response = "Invalid Submission"
                is_correct = None
            context = {'form': form, 'pages': range(puzzle.num_pages),
                      'puzzle': puzzle, 'PROTECTED_URL': settings.PROTECTED_URL,
                      'response': response, 'is_correct': is_correct}
            return render(request, 'puzzle.html', context)

        # If the hunt isn't public and you aren't signed in, please stop...
        if(team is not None):
            return HttpResponse('fail')

        # Normal answer responses for a signed in user in an ongoing hunt
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            s = Submission.objects.create(submission_text=user_answer,
                puzzle=puzzle, submission_time=timezone.now(), team=team)
            response = respond_to_submission(s)

        # Render response to HTML
        submission_list = [render_to_string('puzzle_sub_row.html', {'submission': s})]

        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        # Send back rendered response for display
        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))

    # Will return HTML rows for all submissions the user does not yet have
    elif request.is_ajax():
        if(team is not None):
            return HttpResponseNotFound('access denied')

        # Find which objects the user hasn't seen yet and render them to HTML
        last_date = datetime.strptime(request.GET.get("last_date"), '%Y-%m-%dT%H:%M:%S.%fZ')
        last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
        submissions = Submission.objects.filter(modified_date__gt=last_date)
        submissions = submissions.filter(team=team, puzzle=puzzle)
        submission_list = [render_to_string('puzzle_sub_row.html', {'submission': submission}) for submission in submissions]

        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))

    else:
        # Only allowed access if the hunt is public or if unlocked by team
        if(puzzle.hunt.is_public or (team != None and puzzle in team.unlocked.all()) or request.user.is_staff):
            submissions = puzzle.submission_set.filter(team=team).order_by('pk')
            form = AnswerForm()
            try:
                last_date = Submission.objects.latest('modified_date').modified_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            context = {'form': form, 'pages': range(puzzle.num_pages), 'puzzle': puzzle,
                       'submission_list': submissions, 'PROTECTED_URL': settings.PROTECTED_URL,
                       'last_date': last_date}
            return render(request, 'puzzle.html', context)
        else:
            return render(request, 'access_error.html')


@login_required
def chat(request):
    """
    A view to handle message submissions via POST, handle message update requests via AJAX, and
    render the hunt participant view of the chat.
    """

    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    if request.method == 'POST':
        if(request.POST.get('team_pk') == ""):
            return HttpResponse(status=400)
        if(request.POST.get("is_announcement") == "true" and request.user.is_staff):
            messages = []
            for team in curr_hunt.team_set.all():
                m = Message.objects.create(time=timezone.now(),
                    text="[Anouncement] " + request.POST.get('message'),
                    is_response=(request.POST.get('is_response') == "true"), team=team)
                messages.append(m)
        else:
            team = Team.objects.get(pk=request.POST.get('team_pk'))
            m = Message.objects.create(time=timezone.now(), text=request.POST.get('message'),
                is_response=(request.POST.get('is_response') == "true"), team=team)
            messages = [m]
    else:
        team = team_from_user_hunt(request.user, curr_hunt)
        if(team is not None):
            #TODO maybe handle more nicely because hunt may just not be released
            #return render(request, 'not_released.html', {'reason': "team"})
            return HttpResponse(status=404)
        if request.is_ajax():
            messages = Message.objects.filter(pk__gt=request.GET.get("last_pk"))
        else:
            messages = Message.objects
        messages = messages.filter(team=team).order_by('time')

    message_dict = {}
    for message in messages:
        if message.team.team_name not in message_dict:
            message_dict[message.team.team_name] = {'pk': message.team.pk, 'messages': [message]}
        else:
            message_dict[message.team.team_name]['messages'].append(message)
    for team_name in message_dict:
        message_dict[team_name]['messages'] = render_to_string(
            'chat_messages.html', {'messages': message_dict[team_name]['messages']})
    try:
        last_pk = Message.objects.latest('id').id
    except Message.DoesNotExist:
        last_pk = 0

    context = {'message_dict': message_dict, 'last_pk': last_pk}
    if request.is_ajax() or request.method == 'POST':
        return HttpResponse(json.dumps(context))
    else:
        context['team'] = team.pk
        return render(request, 'chat.html', context)


@login_required
def unlockables(request):
    """ A view to render the unlockables page for hunt participants. """
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    team = team_from_user_hunt(request.user, curr_hunt)
    if(team is not None):
        return render(request, 'not_released.html', {'reason': "team"})
    unlockables = Unlockable.objects.filter(puzzle__in=team.solved.all())
    return render(request, 'unlockables.html', {'unlockables': unlockables, 'team': team})
