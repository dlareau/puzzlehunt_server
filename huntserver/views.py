# Create your views here.
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext, loader
from django.utils import timezone
from subprocess import check_output
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth import authenticate
from django.contrib.admin.views.decorators import staff_member_required
import json

from .models import *
from .forms import *
from .puzzle import *
from .redis import *

def team_from_user_hunt(user, hunt):
    teams = get_object_or_404(Person, user=user).teams.filter(hunt=hunt)
    if(len(teams) > 0):
        return teams[0]
    else:
        return None

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
        if(settings.DEBUG):
            return redirect(settings.MEDIA_URL + file_path)
        response = HttpResponse()
        url = settings.MEDIA_URL + file_path
        # let nginx determine the correct content type 
        response['Content-Type']=""
        # This is what lets django access the normally restricted /static/
        response['X-Accel-Redirect'] = url
        return response
    
    return HttpResponseNotFound('<h1>Page not found</h1>')

def create_account(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    teams = curr_hunt.team_set.all().exclude(team_name="Admin").order_by('pk')
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        pf = PersonForm(request.POST, prefix='person')
        if uf.is_valid() and pf.is_valid():
            user = uf.save()
            person = pf.save(commit=False)
            person.user = user
            person.save()
            return index()
        else:
            return render(request, "create_account.html", {'uf': uf, 'pf': pf, 'teams': teams})
    else:
        uf = UserForm(prefix='user')
        pf = PersonForm(prefix='person')
        return render(request, "create_account.html", {'uf': uf, 'pf': pf, 'teams': teams})

def registration(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    teams = Team.objects.filter(hunt=curr_hunt)
    return render(request, "registration.html", {'teams': teams})

def login_selection(request):
    if 'next' in request.GET:
        context = {'next': request.GET['next']}
    else:
        context = {'next': "/"}
    return render(request, "login_selection.html", context)

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

def current_hunt_info(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    return render(request, "hunt_info.html", {'curr_hunt': curr_hunt})

def index(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    return render(request, "index.html", {'curr_hunt': curr_hunt})

def previous_hunts(request):
    old_hunts = Hunt.objects.all().exclude(hunt_number=settings.CURRENT_HUNT_NUM).order_by('hunt_number')
    return render(request, "previous_hunts.html", {'hunts': old_hunts})

def account_logout(request):
    logout(request)
    if 'next' in request.GET:
        return redirect("/Shibboleth.sso/Logout?return=https://puzzlehunt.club.cc.cmu.edu" + request.GET['next'])
    else:
        return redirect("/Shibboleth.sso/Logout?return=https://puzzlehunt.club.cc.cmu.edu")

@login_required
def puzzle(request, puzzle_id):
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
            respond_to_submission(s)

        return HttpResponse('success')

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
                if(puzzle in solved):
                    sol_array[-1]['cells'].append([solves.get(puzzle=puzzle).submission.submission_time,
                                                   puzzle.puzzle_id])
                # Unlocked => Identify as unlocked, puzzle id, and unlock time
                elif(puzzle in unlocked):                
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
    teams = curr_hunt.team_set.all().order_by("team_name")
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

@login_required
def chat(request):
    if request.method == 'POST':
        if(request.POST.get('team_pk') != ""):
            m = Message.objects.create(time=timezone.now(), text=request.POST.get('message'),
                is_response=(request.POST.get('is_response')=="true"),
                team=Team.objects.get(pk=request.POST.get('team_pk')))
            send_chat_message(m)
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
        return render(request, 'chat.html', {'messages': message_list, 'team':team})

@login_required
def unlockables(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    team = team_from_user_hunt(request.user, curr_hunt)
    if(team == None):
        return render(request, 'not_released.html', {'reason': "team"})
    unlockables = Unlockable.objects.filter(puzzle__in=team.solved.all())
    return render(request, 'unlockables.html', {'unlockables': unlockables, 'team':team})

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

#TODO: fix
@login_required
def public_stats(request):
    newest_hunt = 1
    return hunt(request, newest_hunt)

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
