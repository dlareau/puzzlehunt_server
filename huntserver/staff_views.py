from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Submission, Hunt, Team, Puzzle, Unlock, Solve, Message
from .forms import SubmissionForm, UnlockForm
from .utils import unlock_puzzles, download_puzzles

@staff_member_required
def queue(request, page_num=1):
    # Process admin responses to submissions
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            s = Submission.objects.get(pk=form.cleaned_data['sub_id'])
            s.response_text = response
            s.modified_date = timezone.now()
            s.save()

        return HttpResponse('success')

    else:
        hunt = Hunt.objects.get(is_current_hunt=True)
        submissions = Submission.objects.filter(puzzle__hunt=hunt).select_related('team', 'puzzle').order_by('-pk')
        pages = Paginator(submissions, 30)
        try:
            submissions = pages.page(page_num)
        except PageNotAnInteger:
            submissions = pages.page(1)
        except EmptyPage:
            submissions = pages.page(pages.num_pages)
        form = SubmissionForm()
        try:
            last_date = Submission.objects.latest('modified_date').modified_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        context = {'form': form, 'submission_list': submissions, 'last_date': last_date}
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
            t.save()
        return HttpResponse('success')

    else:
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
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
        try:
            last_solve_pk = Solve.objects.latest('id').id
        except Solve.DoesNotExist:
            last_solve_pk = 0
        try:
            last_unlock_pk = Unlock.objects.latest('id').id
        except Unlock.DoesNotExist:
            last_unlock_pk = 0
        context = {'puzzle_list':puzzles, 'team_list':teams, 'sol_array':sol_array, 
                   'last_unlock_pk': last_unlock_pk, 'last_solve_pk': last_solve_pk}
        return render(request, 'progress.html', context)

@staff_member_required
def charts(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
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
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    messages = Message.objects.filter(team__hunt=curr_hunt).order_by('team', 'time')
    message_list = []
    for message in messages:
        message_list.append({'time': message.time, 'text':message.text,
            'team':{'pk': message.team.pk, 'name': message.team.team_name},
            'is_response': message.is_response})
    try:
        last_pk = Message.objects.latest('id').id
    except Message.DoesNotExist:
        last_pk = 0
    return render(request, 'staff_chat.html', {'messages': message_list, 'last_pk':last_pk})

@staff_member_required
def hunt_management(request):
    hunts = Hunt.objects.all()
    return render(request, 'hunt_management.html', {'hunts': hunts})

# Not actually a page, just various control functions
@staff_member_required
def control(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    if(curr_hunt.is_open):
        teams = curr_hunt.team_set.all().order_by('team_name')
    else:
        teams = currhunt.team_set.filter(playtester=True).orderby('team_name')
    if request.GET.get('initial', None):
        for team in teams:
            unlock_puzzles(team)
        return redirect('huntserver:hunt_management')
    elif request.GET.get('reset', None):
        for team in teams:
            team.unlocked.clear()
            team.unlock_set.all().delete()
            team.solved.clear()
            team.solve_set.all().delete()
            team.submission_set.all().delete()
        return redirect('huntserver:hunt_management')
    elif request.GET.get('getpuzzles', None):
        download_puzzles(Hunt.objects.get(is_current_hunt=True))
        return redirect('huntserver:hunt_management')
    elif request.GET.get('new_current_hunt', None):
        new_curr = Hunt.objects.get(hunt_number=int(request.GET.get('new_current_hunt')))
        new_curr.is_current_hunt = True;
        new_curr.save()
        return redirect('huntserver:hunt_management')
    else:
        return render(request, 'access_error.html')

@staff_member_required
def emails(request):
    teams = Team.objects.filter(hunt__is_current_hunt=True)
    people = []
    for team in teams:
         people = people + list(team.person_set.all())
    email_list = []
    for person in people:
        email_list.append(person.user.email)
    return HttpResponse(", ".join(email_list))

