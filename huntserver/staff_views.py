from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import *
from .forms import *
from .puzzle import *
from .redis import *

@staff_member_required
def queue(request):
    # Process admin responses to submissions
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            s = Submission.objects.get(pk=form.cleaned_data['sub_id'])
            s.response_text = response
            s.save()
            # Update relevant parties
            send_submission_update(s)

        return HttpResponse('success')

    else:
        hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
        submissions = Submission.objects.filter(puzzle__hunt=hunt).select_related('team', 'puzzle').order_by('pk')
        form = SubmissionForm()
        context = {'form': form, 'submission_list': submissions}
        return render(request, 'queue.html', context)

@staff_member_required
def progress(request):
    # Admin unlocking a puzzle
    if request.method == 'POST':
        form = UnlockForm(request.POST)
        if form.is_valid():
            t = Team.objects.get(pk=form.cleaned_data['team_id'])
            p = Puzzle.objects.get(puzzle_id=form.cleaned_data['puzzle_id'])
            Unlock.objects.create(team=t, puzzle=p, time=timezone.now())
            send_status_update(p, t, "unlock")
            t.save()
        return HttpResponse('success')

    else:
        curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
        teams = curr_hunt.team_set.all().order_by('team_name')
        puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
        # An array of solves, organized by team then by puzzle
        # This array is essentially the grid on the progress page
        # The structure is messy, it was built part by part as features were added
        sol_array = []
        for team in teams:
            # These are defined to reduce DB queries
            solved = team.solved.all()
            unlocked = team.unlocked.all()
            solves = team.solve_set.select_related('submission')
            unlocks = team.unlock_set.all()

            # Basic team information for row headers
            # The last element ('cells') is an array of the row's data
            sol_array.append({'team':team, 'num':len(solved), 'cells':[]})
            # What goes in each cell (item in "cells") is based on puzzle status
            for puzzle in puzzles:
                # Solved => solve object and puzzle id
                if puzzle in solved:
                    sol_array[-1]['cells'].append([solves.get(puzzle=puzzle).submission.submission_time,
                                                   puzzle.puzzle_id])
                # Unlocked => Identify as unlocked, puzzle id, and unlock time
                elif puzzle in unlocked:
                    unlock_time = unlocks.get(puzzle=puzzle).time
                    sol_array[-1]['cells'].append(["unlocked", puzzle.puzzle_id, unlock_time])
                # Locked => Identify as locked and puzzle id
                else:
                    sol_array[-1]['cells'].append(["locked", puzzle.puzzle_id])
        context = {'puzzle_list':puzzles, 'team_list':teams, 'sol_array':sol_array}
        return render(request, 'progress.html', context)

@staff_member_required
def charts(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
    puzzle_info_dicts = []
    for puzzle in puzzles:
        puzzle_info_dicts.append({
            "name": puzzle.puzzle_name,
            "locked": curr_hunt.team_set.count()-puzzle.unlocked_for.filter(unlock__puzzle__hunt=curr_hunt).count(),
            "unlocked": puzzle.unlocked_for.count() - puzzle.solved_for.count(),
            "solved": puzzle.solved_for.count()
            })

    context = {'data1_list':puzzle_info_dicts}
    return render(request, 'charts.html', context)

@staff_member_required
def admin_chat(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    messages = Message.objects.filter(team__hunt=curr_hunt).order_by('team', 'time')
    message_list = []
    for message in messages:
        message_list.append({'time': message.time, 'text':message.text,
            'team':{'pk': message.team.pk, 'name': message.team.team_name},
            'is_response': message.is_response})
    return render(request, 'staff_chat.html', {'messages': message_list})

# Not actually a page, just various control functions
@staff_member_required
def control(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    teams = curr_hunt.team_set.all().order_by('team_name')
    if request.GET.get('initial'):
        for team in teams:
            unlock_puzzles(team)
        return redirect('huntserver:progress')
    elif request.GET.get('reset'):
        for team in teams:
            team.unlocked.clear()
            team.unlock_set.all().delete()
            team.solved.clear()
            team.solve_set.all().delete()
            team.submission_set.all().delete()
        return redirect('huntserver:progress')
    elif request.GET.get('getpuzzles'):
        download_puzzles(Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM))
        return redirect('huntserver:progress')
    else:
        return render(request, 'access_error.html')

@staff_member_required
def emails(request):
    teams = Team.filter(hunt__hunt_number=settings.CURRENT_HUNT_NUM)
    people = []
    for team in teams:
        people = people.append(team.person_set.all())
    emails = []
    for person in people:
        emails.append(person.user.email)
    return HttpResponse(", ".join(emails))

