from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from datetime import datetime
from dateutil import tz
import json
import os

from .models import Puzzle, Hunt, Submission, Message, Team, Solve, Unlock, Unlockable
from .forms import AnswerForm
from .utils import respond_to_submission, team_from_user_hunt, dummy_team_from_hunt

@login_required
def protected_static(request, file_path):
    allowed = False
    levels = file_path.split("/")
    if(levels[0] == "puzzles"):
        puzzle_id = levels[1][0:3]
        puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
        team = team_from_user_hunt(request.user, puzzle.hunt)
        # Only allowed access to the image if the puzzle is unlocked
        if (puzzle.hunt.is_public or request.user.is_staff or
           (team != None and puzzle in team.unlocked.all())):
            allowed = True
    else:
        allowed = True

    if allowed:
        #if(settings.DEBUG):
        #    return redirect(settings.MEDIA_URL + file_path)
        response = HttpResponse()
        # let apache determine the correct content type
        response['Content-Type']=""
        # This is what lets django access the normally restricted /static/
        response['X-Sendfile'] = smart_str(os.path.join(settings.MEDIA_ROOT, file_path))
        return response

    return HttpResponseNotFound('<h1>Page not found</h1>')

@login_required
def hunt(request, hunt_num):
    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    team = team_from_user_hunt(request.user, hunt)

    # Admins get all access, wrong teams/early lookers get an error page
    # real teams get appropriate puzzles, and puzzles from past hunts are public
    if(request.user.is_staff):
        puzzle_list = hunt.puzzle_set.all()
    # Hunt has not yet started
    elif(hunt.is_locked):
        return render(request, 'not_released.html', {'reason': "locked"})
    # Hunt has started
    elif(hunt.is_open):
        # see if the team does not belong to the hunt being accessed
        if(team.is_normal_team and (team == None or team.hunt != hunt)):
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
    if(team == None):
        solved = []
    else:
        solved = team.solved.all()
    context = {'hunt': hunt, 'puzzles': puzzles, 'team': team, 'solved': solved}

    # Each hunt should have a main template named hunt#.html (ex: hunt3.html)
    return render(request, 'hunt' + str(hunt_num) + '.html', context)

@login_required
def current_hunt(request):
    return hunt(request, Hunt.objects.get(is_current_hunt=True).hunt_number)

@login_required
def puzzle_view(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id__iexact=puzzle_id)
    team = team_from_user_hunt(request.user, puzzle.hunt)

    # Create submission object and then rely on utils.respond_to_submission
    # for automatic responses.
    if request.method == 'POST':
        if(puzzle.hunt.is_public):
            form = AnswerForm(request.POST)
            team = dummy_team_from_hunt(puzzle.hunt)
            if form.is_valid():
                user_answer = form.cleaned_data['answer']
                s = Submission.objects.create(submission_text = user_answer,
                    puzzle = puzzle, submission_time = timezone.now(), team = team)
                response = respond_to_submission(s)
            else:
                response = "Invalid Submission"
            context = {'form': form, 'pages': range(puzzle.num_pages),
                      'puzzle': puzzle, 'PROTECTED_URL': settings.PROTECTED_URL,
                      'response': response}
            return render(request, 'puzzle.html', context)
        if(team == None):
            return HttpResponse('fail')
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            s = Submission.objects.create(submission_text = user_answer,
                puzzle = puzzle, submission_time = timezone.now(), team = team)
            # TODO: might be fine with just respond_to_submission
            response = respond_to_submission(s)

        submission_list = [render_to_string('puzzle_sub_row.html', {'submission': s})]

        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))

    elif request.is_ajax():
        if(team == None):
            return HttpResponseNotFound('access denied')

        last_date = datetime.strptime(request.GET.get("last_date"), '%Y-%m-%dT%H:%M:%S.%fZ')
        last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
        submissions = Submission.objects.filter(modified_date__gt = last_date)
        submissions = submissions.filter(team=team)
        submission_list = [render_to_string('puzzle_sub_row.html', {'submission': submission}) for submission in submissions]

        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))

    else:
        # Only allowed access if the hunt is public or if unlocked by team
        if(puzzle.hunt.is_public or (team != None and puzzle in team.unlocked.all())):
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
    # Generate messages depending on what we are doing.
    if request.method == 'POST':
        if(request.POST.get('team_pk') == ""):
            return HttpResponse(status=400)
        team = Team.objects.get(pk=request.POST.get('team_pk'))
        m = Message.objects.create(time=timezone.now(), text=request.POST.get('message'),
            is_response=(request.POST.get('is_response')=="true"), team=team)
        messages = [m]
    else:
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
        team = team_from_user_hunt(request.user, curr_hunt)
        if(team == None):
            #TODO maybe handle more nicely because hunt may just not be released
            #return render(request, 'not_released.html', {'reason': "team"})
            return HttpResponse(status=404)
        if request.is_ajax():
            messages = Message.objects.filter(pk__gt = request.GET.get("last_pk"))
        else:
            messages = Message.objects
        messages = messages.filter(team=team).order_by('time')

    message_dict = {}
    message_dict[team.team_name] = {'pk': team.pk, 'messages': list(messages)}
    message_dict[team.team_name]['messages'] = render_to_string('chat_messages.html', {'messages': message_dict[team.team_name]['messages']})
    try:
        last_pk = Message.objects.latest('id').id
    except Message.DoesNotExist:
        last_pk = 0


    context = {'message_dict': message_dict, 'last_pk':last_pk}
    if request.is_ajax() or request.method == 'POST':
        return HttpResponse(json.dumps(context))
    else:
        return render(request, 'chat.html', context)

@login_required
def unlockables(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    team = team_from_user_hunt(request.user, curr_hunt)
    if(team == None):
        return render(request, 'not_released.html', {'reason': "team"})
    unlockables = Unlockable.objects.filter(puzzle__in=team.solved.all())
    return render(request, 'unlockables.html', {'unlockables': unlockables, 'team':team})
