from django.conf import settings
from django.core import serializers
from django.utils.html import escape
from django.utils.dateformat import DateFormat
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.encoding import smart_str
from datetime import datetime
from dateutil import tz
import json
import os
time_zone = tz.gettz(settings.TIME_ZONE)

from utils import team_from_user_hunt
from .models import *
from .forms import *
from .puzzle import *

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
        url = settings.MEDIA_URL + file_path
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
        if(team == None or team.hunt != hunt):
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
    context = {'puzzles': puzzles, 'team': team, 'solved': solved}
    
    # Each hunt should have a main template named hunt#.html (ex: hunt3.html)
    return render(request, 'hunt' + str(hunt_num) + '.html', context)

@login_required
def current_hunt(request):
    return hunt(request, settings.CURRENT_HUNT_NUM)

@login_required
def puzzle_view(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id__iexact=puzzle_id)
    team = team_from_user_hunt(request.user, puzzle.hunt)

    # Create submission object and then rely on puzzle.py->respond_to_submission
    # for automatic responses.
    if request.method == 'POST':
        if(team == None):
            return HttpResponse('fail')
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            s = Submission.objects.create(submission_text = user_answer, 
                puzzle = puzzle, submission_time = timezone.now(), team = team)
            response = respond_to_submission(s)

        return HttpResponse(response)

    else:
        # Only allowed access if the hunt is public or if unlocked by team
        if(puzzle.hunt.is_public or (team != None and puzzle in team.unlocked.all())):
            submissions = puzzle.submission_set.filter(team=team).order_by('pk')
            form = AnswerForm()
            context = {'form': form, 'pages': range(puzzle.num_pages), 'puzzle': puzzle, 
                       'submission_list': submissions, 'PROTECTED_URL': settings.PROTECTED_URL}
            return render(request, 'puzzle.html', context)
        else:
            return render(request, 'access_error.html')

@login_required
def chat(request):
    if request.method == 'POST':
        if(request.POST.get('team_pk') != ""):
            m = Message.objects.create(time=timezone.now(), text=request.POST.get('message'),
                is_response=(request.POST.get('is_response')=="true"),
                team=Team.objects.get(pk=request.POST.get('team_pk')))
        return HttpResponse('success')
    else:
        curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
        team = team_from_user_hunt(request.user, curr_hunt)
        if(team == None):
            return render(request, 'not_released.html', {'reason': "team"})
        messages = Message.objects.filter(team=team).order_by('time')
        message_list = []
        for message in messages:
            message_list.append({'time': message.time, 'text':message.text,
                'team':message.team, 'is_response': message.is_response})
        last_pk = Message.objects.latest('id').id
        return render(request, 'chat.html', {'messages': message_list, 'team':team, 'last_pk':last_pk})


@login_required
def ajax(request, ajax_type):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    team = team_from_user_hunt(request.user, curr_hunt)
    if(team == None):
        return HttpResponseNotFound('access denied')
    if(ajax_type == "message" and "last_pk" in request.GET):
        last_pk = request.GET.get("last_pk")
        results = Message.objects.filter(pk__gt = last_pk)
        if(not request.user.is_staff):
            results = results.filter(team=team)
        results = list(results.all())
        if(len(results) > 0):
            for i in range(len(results)):
                message = dict()
                message['team_pk'] = results[i].team.pk
                message['team_name'] = results[i].team.team_name
                message['text'] = escape(results[i].text)
                message['is_response'] = results[i].is_response
                df = DateFormat(results[i].time.astimezone(time_zone))
                message['time'] = df.format("h:i a")
                results[i] = message
            results.append(Message.objects.latest('id').id)
    elif(ajax_type == "submission"):
        results1 = Submission.objects.none()
        results2 = Submission.objects.none()
        if("last_pk" in request.GET):
            last_pk = request.GET.get("last_pk")
            results1 = Submission.objects.filter(pk__gt = last_pk)
        if("last_date" in request.GET):
            last_date = datetime.strptime(request.GET.get("last_date"), '%Y-%m-%dT%H:%M:%SZ')
            last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
            results2 = Submission.objects.filter(modified_date__gt = last_date)
        results = results1 | results2
        if(not (request.user.is_staff and "all" in request.GET)):
            results = results.filter(team=team)
        results = list(results.all())
        if(len(results) > 0):
            for i in range(len(results)):
                modelJSON = json.loads(serializers.serialize("json", [results[i]]))[0]
                message = modelJSON['fields']
                message['response_text'] = escape(message['response_text'])
                message['puzzle'] = results[i].puzzle.puzzle_id
                message['puzzle_name'] = results[i].puzzle.puzzle_name
                message['team'] = results[i].team.team_name
                message['pk'] = modelJSON['pk']
                df = DateFormat(results[i].submission_time.astimezone(time_zone))
                message['time_str'] = df.format("h:i a")
                results[i] = message
            results.append(Submission.objects.latest('id').id)
    elif(ajax_type == "progress" and "last_solve_pk" in request.GET and 
          "last_unlock_pk" in request.GET):
        results = []
        if(not request.user.is_staff):
            return HttpResponseNotFound('access denied')
        last_solve_pk = request.GET.get("last_solve_pk")
        last_unlock_pk = request.GET.get("last_unlock_pk")
        solves = list(Solve.objects.filter(pk__gt = last_solve_pk))
        unlocks = list(Unlock.objects.filter(pk__gt = last_unlock_pk))
        for i in range(len(unlocks)):
            message = dict()
            message['puzzle_id'] = unlocks[i].puzzle.puzzle_id
            message['puzzle_num'] = unlocks[i].puzzle.puzzle_number
            message['puzzle_name'] = unlocks[i].puzzle.puzzle_name
            message['team_pk'] = unlocks[i].team.pk
            message['status_type'] = "unlock"
            results.append(message)
        for i in range(len(solves)):
            message = dict()
            message['puzzle_id'] = solves[i].puzzle.puzzle_id
            message['puzzle_num'] = solves[i].puzzle.puzzle_number
            message['puzzle_name'] = solves[i].puzzle.puzzle_name
            message['team_pk'] = solves[i].team.pk
            message['status_type'] = "solve"
            try:
                time = solves[i].team.solve_set.filter(puzzle=solves[i].puzzle)[0].submission.submission_time
                df = DateFormat(time.astimezone(time_zone))
                message['time_str'] = df.format("h:i a")
            except:
                message['time_str'] = "0:00 am"
            results.append(message)
        if(len(results) > 0):
            results.append(Solve.objects.latest('id').id)
            results.append(Unlock.objects.latest('id').id)
    else:
        results = []
    response = json.dumps(results)
    return HttpResponse(response)

@login_required
def unlockables(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    team = team_from_user_hunt(request.user, curr_hunt)
    if(team == None):
        return render(request, 'not_released.html', {'reason': "team"})
    unlockables = Unlockable.objects.filter(puzzle__in=team.solved.all())
    return render(request, 'unlockables.html', {'unlockables': unlockables, 'team':team})
