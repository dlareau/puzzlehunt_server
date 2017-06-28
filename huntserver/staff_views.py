from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
import json
from datetime import datetime
from dateutil import tz
import networkx as nx
from django.core.mail import send_mail, EmailMessage

from .models import Submission, Hunt, Team, Puzzle, Unlock, Solve, Message
from .forms import SubmissionForm, UnlockForm, EmailForm
from .utils import unlock_puzzles, download_puzzles

@staff_member_required
def queue(request, page_num=1):
    # Process admin responses to submissions
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        if not form.is_valid():
            return HttpResponse(status=400)
        response = form.cleaned_data['response']
        s = Submission.objects.get(pk=form.cleaned_data['sub_id'])
        s.response_text = response
        s.modified_date = timezone.now()
        s.save()
        submissions = [s]

    elif request.is_ajax():
        last_date = datetime.strptime(request.GET.get("last_date"), '%Y-%m-%dT%H:%M:%S.%fZ')
        last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
        submissions = Submission.objects.filter(modified_date__gt = last_date)

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
    submission_list = [render_to_string('queue_row.html', {'submission': submission}, request=request) for submission in submissions]

    if request.is_ajax() or request.method == 'POST':
        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))
    else:
        context = {'form': form, 'page_info': submissions,
        'submission_list': submission_list, 'last_date': last_date}
        return render(request, 'queue.html', context)

@staff_member_required
def progress(request):
    # Admin unlocking a puzzle
    if request.method == 'POST':
        form = UnlockForm(request.POST)
        if form.is_valid():
            t = Team.objects.get(pk=form.cleaned_data['team_id'])
            p = Puzzle.objects.get(puzzle_id=form.cleaned_data['puzzle_id'])
            u = Unlock.objects.create(team=t, puzzle=p, time=timezone.now())
            return HttpResponse(json.dumps(u.serialize_for_ajax()))
        return HttpResponse(status=400)

    elif request.is_ajax():
        update_info = []
        if not ("last_solve_pk" in request.GET and
                "last_unlock_pk" in request.GET):
            return HttpResponse(status=404)
        results = []
        if(not request.user.is_staff):
            return HttpResponseNotFound('access denied')

        last_solve_pk = request.GET.get("last_solve_pk")
        solves = list(Solve.objects.filter(pk__gt = last_solve_pk))
        for i in range(len(solves)):
            results.append(solves[i].serialize_for_ajax())

        last_unlock_pk = request.GET.get("last_unlock_pk")
        unlocks = list(Unlock.objects.filter(pk__gt = last_unlock_pk))
        for i in range(len(unlocks)):
            results.append(unlocks[i].serialize_for_ajax())

        if(len(results) > 0):
            update_info = [Solve.objects.latest('id').id]
            update_info.append(Unlock.objects.latest('id').id)
        response = json.dumps({'messages': results, 'update_info': update_info})
        return HttpResponse(response)

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
    if request.is_ajax():
        last_pk = request.GET.get("last_pk")
        messages = Message.objects.filter(pk__gt = last_pk)
    else:
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
        messages = Message.objects.filter(team__hunt=curr_hunt).order_by('team', 'time').select_related('team')

    team_name = ""
    message_dict = {}
    for message in messages:
        if message.team.team_name != team_name:
            team_name = message.team.team_name
            message_dict[team_name] = {'pk': message.team.pk, 'messages': []}
        message_dict[team_name]['messages'].append(message)
    for team in message_dict:
        message_dict[team]['messages'] = render_to_string('chat_messages.html', {'messages': message_dict[team]['messages']})
    try:
        last_pk = Message.objects.latest('id').id
    except Message.DoesNotExist:
        last_pk = 0


    context = {'message_dict': message_dict, 'last_pk':last_pk}
    if request.is_ajax():
        return HttpResponse(json.dumps(context))
    else:
        return render(request, 'staff_chat.html', context)

@staff_member_required
def hunt_management(request):
    hunts = Hunt.objects.all()
    return render(request, 'hunt_management.html', {'hunts': hunts})

@staff_member_required
def control(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    if(curr_hunt.is_open):
        teams = curr_hunt.team_set.all().order_by('team_name')
    else:
        teams = curr_hunt.team_set.filter(playtester=True).order_by('team_name')
    if(request.method == 'POST' and "action" in request.POST):
        if(request.POST["action"] == "initial"):
            for team in teams:
                unlock_puzzles(team)
            return redirect('huntserver:hunt_management')
        if(request.POST["action"] == "reset"):
            for team in teams:
                team.unlocked.clear()
                team.unlock_set.all().delete()
                team.solved.clear()
                team.solve_set.all().delete()
                team.submission_set.all().delete()
            return redirect('huntserver:hunt_management')
        if(request.POST["action"] == "getpuzzles"):
            download_puzzles(Hunt.objects.get(is_current_hunt=True))
            return redirect('huntserver:hunt_management')
        if(request.POST["action"] == "new_current_hunt"):
            new_curr = Hunt.objects.get(hunt_number=int(request.POST.get('hunt_num')))
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
    email_list = [person.user.email for person in people]

    if request.method == 'POST':
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            subject = email_form.cleaned_data['subject']
            message = email_form.cleaned_data['message']
            email_to_chunks = [email_list[x:x+20] for x in xrange(0, len(email_list), 20)]
            for to_chunk in email_to_chunks:
                email = EmailMessage(subject, message,'puzzlehuntcmu@gmail.com',
                     to_chunk, [])
                email.send()
            return HttpResponseRedirect('')
    else:
        email_form = EmailForm()
    context = {'email_list': (', ').join(email_list), 'email_form': email_form}
    return render(request, 'email.html', context)

@staff_member_required
def depgraph(request):
    hunt = Hunt.objects.get(is_current_hunt=True)
    G=nx.DiGraph()
    for puzzle in hunt.puzzle_set.all():
        for unlock in puzzle.unlocks.all():
            G.add_edge(unlock.puzzle_number, puzzle.puzzle_number)
    edges = [line.split(' ') for line in nx.generate_edgelist(G, data=False)]
    context = {'puzzles': hunt.puzzle_set.all(), 'edges': edges}
    return render(request, 'depgraph.html', context)
