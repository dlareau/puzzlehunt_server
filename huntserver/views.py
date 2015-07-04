# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext, loader
from django.utils import timezone
import json

from .models import *
from .forms import *
from .puzzle import *
from .redis import *

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
            s.response_text = respond_to_submission(s, puzzle)
            s.save()
            if(s.response_text == "Correct!"):
                Solve.objects.create(puzzle=s.puzzle, team=s.team, submission=s)
                send_status_update(puzzle, team, "solve")
            s.save()
            send_submission_update(s)
            unlock_puzzles(team)
        return redirect('huntserver:puzzle', puzzle_id=puzzle_id)

    #If not a submission, just render the puzzle page
    else:
        submissions = puzzle.submission_set.filter(team=team).order_by('pk')
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

@login_required
def progress(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    teams = curr_hunt.team_set.all().order_by('team_name')
    if request.GET.get('initial'):
        for team in teams:
            unlock_puzzles(team)
        return redirect('huntserver:progress')
    elif request.GET.get('reset'):
        for team in teams:
            team.unlocked.clear()
            team.solved.clear()
            team.solve_set.all().delete()
            team.submission_set.all().delete()
        return redirect('huntserver:progress')
    else:
        puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
        sol_array = []
        for team in teams:
            sol_array.append({'team':team, 'num':len(team.solved.all()), 'cells':[]})
            for puzzle in puzzles:
                if(puzzle in team.solved.all()):
                    sol_array[-1]['cells'].append([team.solve_set.filter(puzzle=puzzle)[0], puzzle.puzzle_id])
                elif(puzzle in team.unlocked.all()):                
                    sol_array[-1]['cells'].append(["unlocked", puzzle.puzzle_id])
                else:
                    sol_array[-1]['cells'].append(["locked", puzzle.puzzle_id])
        context = {'puzzle_list':puzzles, 'team_list':teams, 'sol_array':sol_array}
        return render(request, 'progress.html', context)

@login_required
def unlock(request):
    if request.method == 'POST':
        form = UnlockForm(request.POST)
        if form.is_valid():
            t = Team.objects.get(pk=form.cleaned_data['team_id'])
            p = Puzzle.objects.get(puzzle_id=form.cleaned_data['puzzle_id'])
            t.unlocked.add(p)
            send_status_update(p, t, "unlock")
            t.save()
        return redirect('huntserver:progress')
    
    else:   
        return hunt(request, settings.CURRENT_HUNT_NUM)

#TODO: fix
@login_required
def public_stats(request):
    newest_hunt = 1
    return hunt(request, newest_hunt)
