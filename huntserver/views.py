# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext, loader
from django.utils import timezone
from subprocess import check_output
from django.http import HttpResponse
from django.contrib.auth import authenticate

from .models import *
from .forms import *
from .puzzle import *
from .redis import *

def is_admin(request):
    if request.user.is_authenticated():
        if request.user.username == settings.ADMIN_ACCT:
            return True
    return False

def registration(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    if(request.method == 'POST'):
        # Check for correct password when doing existing registration
        if(request.POST.get("validate")):
            team = curr_hunt.team_set.get(team_name=request.POST.get("team_name"))
            if(len(team.person_set.all()) >= team.hunt.team_size):
                return HttpResponse('fail-full')
            user = authenticate(username=team.login_info.username, password=request.POST.get("password"))
            if user is not None:
                return HttpResponse('success')
            else:
                return HttpResponse('fail-password')
                
        # Check if team already exists when doing new registration
        elif(request.POST.get("check")):
            print(curr_hunt.team_set.all())
            if(curr_hunt.team_set.filter(team_name__iexact=request.POST.get("team_name")).exists()):
                return HttpResponse('fail')
            else:
                return HttpResponse('success')

        # Create new team and person
        elif(request.POST.get("new")):
            form = RegistrationForm(request.POST)
            if (form.is_valid()):
                if(form.cleaned_data['password'] == form.cleaned_data['confirm_password']):
                    u = User.objects.create_user(form.cleaned_data['username'], 
                        password=form.cleaned_data['password'])
                    t = Team.objects.create(team_name = form.cleaned_data['team_name'], 
                        login_info = u, hunt = curr_hunt)
                    p = Person.objects.create(first_name = form.cleaned_data['first_name'], 
                        last_name = form.cleaned_data['last_name'], 
                        email = form.cleaned_data['email'], 
                        phone = form.cleaned_data['phone'], 
                        comments = "Dietary Restrictions: " + form.cleaned_data['dietary_issues'], team = t)
            return HttpResponse('success')

        # Find existing team and add person. 
        elif(request.POST.get("existing")):
            form = RegistrationForm(request.POST)
            if form.is_valid():
                if(len(team.person_set.all()) < team.hunt.team_size):
                    team = curr_hunt.team_set.get(team_name=form.cleaned_data["team_name"])
                    p = Person.objects.create(first_name = form.cleaned_data['first_name'], 
                        last_name = form.cleaned_data['last_name'], 
                        email = form.cleaned_data['email'], 
                        phone = form.cleaned_data['phone'], 
                    comments = "Dietary Restrictions: " + form.cleaned_data['dietary_issues'], team = team)
            return HttpResponse('success')
        else:
            return HttpResponse('fail')
    else:
        form = RegistrationForm()
        teams = curr_hunt.team_set.all().exclude(team_name="Admin").order_by('team_name')
        return render(request, "registration.html", {'form': form, 'teams': teams})

@login_required
def hunt(request, hunt_num):
    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    team = Team.objects.get(login_info=request.user)
    
    # Show all puzzles from old hunts to anybody
    if(is_admin(request)):
        puzzle_list = hunt.puzzle_set.all()
    elif(hunt.is_locked):
        return render(request, 'not_released.html', {'reason': "locked"})
    elif(hunt.is_open):
        if(team.hunt != hunt):
            return render(request, 'not_released.html', {'reason': "team"})
        else:
            puzzle_list = team.unlocked.filter(hunt=hunt)
    elif(hunt.is_public):
        puzzle_list = hunt.puzzle_set.all()
    else:
        return render(request, 'access_error.html')
        
    puzzles = sorted(puzzle_list, key=lambda p: p.puzzle_number)

    context = {'puzzles': puzzles, 'team': team}
    
    # Each hunt should have a main template named hunt#.html (ex: hunt3.html)
    return render(request, 'hunt' + str(hunt_num) + '.html', context)


@login_required
def index(request):
    return hunt(request, settings.CURRENT_HUNT_NUM)


@login_required
def puzzle(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
    team = Team.objects.get(login_info=request.user);

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            s = Submission.objects.create(submission_text = user_answer, 
                puzzle = puzzle, submission_time = timezone.now(), team = team)
            respond_to_submission(s)

        return redirect('huntserver:puzzle', puzzle_id=puzzle_id)

    else:
        curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
        if(puzzle.hunt.is_public or puzzle in team.unlocked.all()):
            submissions = puzzle.submission_set.filter(team=team).order_by('pk')
            form = AnswerForm()
            directory = "/home/hunt/puzzlehunt_server/huntserver/static/huntserver/puzzles"
            file_str = directory + "/" +  puzzle.puzzle_id + ".pdf"
            pages = int(check_output("pdfinfo " + file_str + " | grep Pages | awk '{print $2}'", shell=True))
            page_range=range(pages)
            context = {'form': form, 'pages': page_range, 'puzzle': puzzle, 
                       'submission_list': submissions}
            return render(request, 'puzzle.html', context)
        else:
            return render(request, 'access_error.html')


@login_required
def queue(request):
    if(not is_admin(request)):
        return render(request, 'access_error.html')

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
        hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
        submissions = Submission.objects.filter(puzzle__hunt=hunt).order_by('pk')
        form = SubmissionForm()
        context = {'form': form, 'submission_list': submissions}
        return render(request, 'queue.html', context)

# This is a big one
@login_required
def progress(request):
    if(not is_admin(request)):
        return render(request, 'access_error.html')

    if request.method == 'POST':
        form = UnlockForm(request.POST)
        if form.is_valid():
            t = Team.objects.get(pk=form.cleaned_data['team_id'])
            p = Puzzle.objects.get(puzzle_id=form.cleaned_data['puzzle_id'])
            Unlock.objects.create(team=t, puzzle=p, time=timezone.now())
            send_status_update(p, t, "unlock")
            t.save()
        return redirect('huntserver:progress')

    else:
        curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
        teams = curr_hunt.team_set.all().order_by('team_name')
        puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
        sol_array = []
        for team in teams:
            sol_array.append({'team':team, 'num':len(team.solved.all()), 'cells':[]})
            for puzzle in puzzles:
                if(puzzle in team.solved.all()):
                    sol_array[-1]['cells'].append([team.solve_set.filter(puzzle=puzzle)[0], puzzle.puzzle_id])
                elif(puzzle in team.unlocked.all()):                
                    unlock_time = team.unlock_set.filter(puzzle=puzzle)[0].time
                    sol_array[-1]['cells'].append(["unlocked", puzzle.puzzle_id, unlock_time])
                else:
                    sol_array[-1]['cells'].append(["locked", puzzle.puzzle_id])
        context = {'puzzle_list':puzzles, 'team_list':teams, 'sol_array':sol_array}
        return render(request, 'progress.html', context)

@login_required
def charts(request):
    if(not is_admin(request)):
        return render(request, 'access_error.html')

    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
    #submissions = Submission.objects.filter(puzzle__hunt=curr_hunt).all().order_by('submission_time')
    #solves = Solve.objects.filter(puzzle__curr_hunt).all().order_by("submission__submission_time")
    teams = curr_hunt.team_set.all().order_by("team_name")
    puzzle_info_dicts = []
    for puzzle in puzzles:
        puzzle_info_dicts.append({
            "name": puzzle.puzzle_name,
            "locked": curr_hunt.team_set.count()-puzzle.unlocked_for.count(),
            "unlocked": puzzle.unlocked_for.count() - puzzle.solved_for.count(),
            "solved": puzzle.solved_for.count()
            })
#    submission_dicts = []
#    for submission in submissions:
#        print(submission.submission_text)
#    solve_dicts = []
#    for team in teams:
#        team_solves = team.solve_set.all().order_by("submission__submission_time")
#        for solve in team_solves:
            
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
        return redirect('huntserver:chat')
    else:
        team = Team.objects.get(login_info=request.user)
        messages = Message.objects.filter(team=team).order_by('time')
        message_list = []
        for message in messages:
            message_list.append({'time': message.time, 'text':message.text,
                'team':message.team, 'is_response': message.is_response})
        return render(request, 'chat.html', {'messages': message_list, 'team':team})

@login_required
def unlockables(request):
    team = Team.objects.get(login_info=request.user)
    unlockables = Unlockable.objects.filter(puzzle__in=team.solved.all())
    return render(request, 'unlockables.html', {'unlockables': unlockables})

@login_required
def admin_chat(request):
    if(not is_admin(request)):
        return render(request, 'access_error.html')

    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    messages = Message.objects.filter(team__hunt=curr_hunt).order_by('team', 'time')
    message_list = []
    for message in messages:
        message_list.append({'time': message.time, 'text':message.text,
            'team':{'pk': message.team.pk, 'name': message.team.team_name},
            'is_response': message.is_response})
    return render(request, 'staff_chat.html', {'messages': message_list})

@login_required
def control(request):
    if(not is_admin(request)):
        return render(request, 'access_error.html')
    
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
