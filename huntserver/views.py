# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext, loader
from django.utils import timezone
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
import json

from .models import Hunt, Puzzle, Submission, Team, Person
from .forms import AnswerForm, SubmissionForm

def send_submission_update(s):
    redis_publisher = RedisPublisher(facility='puzzle_submissions',
                                     users=[s.team.login_info.username, settings.ADMIN_ACCT])
    modelJSON = json.loads(serializers.serialize("json", [s]))[0]
    message = modelJSON['fields']
    message['puzzle'] = s.puzzle.puzzle_id
    message['puzzle_name'] = s.puzzle.puzzle_name
    message['team'] = s.team.team_name
    message['pk'] = modelJSON['pk']
    message = RedisMessage(json.dumps(message))
    redis_publisher.publish_message(message)

@login_required
def hunt(request, hunt_num):
    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)

    # Show all puzzles from old hunts to anybody
    if(hunt.hunt_number == settings.CURRENT_HUNT_NUM):
        team = Team.objects.get(login_info=request.user)
        puzzle_list = team.unlocked.filter(hunt=hunt)
    else:
        puzzle_list = hunt.puzzle_set.all()
        
    puzzles = sorted(puzzle_list, key=lambda p: p.puzzle_number)

    # Each hunt should have a main template named hunt#.html (ex: hunt3.html)
    return render(request, 'hunt' + str(hunt_num) + '.html', {'puzzles': puzzles})

@login_required
def index(request):
    return hunt(request, settings.CURRENT_HUNT_NUM)

@login_required
def puzzle(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
    team = Team.objects.get(login_info=request.user);

    #Puzzles submissions come in as post requests
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            s = Submission(submission_text = user_answer, puzzle = puzzle,
                           submission_time = timezone.now(), team = team)
            if(puzzle.answer.lower() == user_answer.lower()):
                s.response_text = "Correct!"
            s.save()

            #get websocket publisher for admin and the user
            send_submission_update(s)

        return redirect('huntserver:puzzle', puzzle_id=puzzle_id)

    #If not a submission, just render the puzzle page
    else:
        submissions = puzzle.submission_set.filter(team=team)
        form = AnswerForm()
        context = {'form': form, 'puzzle': puzzle, 'submission_list': submissions}
        return render(request, 'puzzle.html', context)

@login_required
def queue(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            s = Submission.objects.get(pk=form.cleaned_data['sub_id'])
            s.response_text = response
            s.save()
            send_submission_update(s)

        return redirect('huntserver:queue')
    
    else:   
        hunt = get_object_or_404(Hunt, hunt_number=settings.CURRENT_HUNT_NUM)
        submissions = Submission.objects.filter(puzzle__hunt=hunt).order_by('pk')
        form = SubmissionForm()
        context = {'form': form, 'submission_list': submissions}
        return render(request, 'queue.html', context)

#TODO: fix
@login_required
def public_stats(request):
    newest_hunt = 1
    return hunt(request, newest_hunt)
