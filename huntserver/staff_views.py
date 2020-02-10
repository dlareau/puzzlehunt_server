from datetime import datetime
from dateutil import tz
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import F
import itertools
import json

from .models import Submission, Hunt, Team, Puzzle, Unlock, Solve, Message, Prepuzzle, Hint
from .forms import SubmissionForm, UnlockForm, EmailForm, HintResponseForm
from .utils import unlock_puzzles, download_puzzle, download_zip


def add_apps_to_context(context, request):
    context['available_apps'] = admin.site.get_app_list(request)
    return context


@staff_member_required
def queue(request):
    """
    A view to handle queue response updates via POST, handle submission update requests via AJAX,
    and render the queue page. Submissions are pre-rendered for standard and AJAX requests.
    """

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
        submissions = Submission.objects.filter(modified_date__gt=last_date)
        submissions = submissions.exclude(team__location="DUMMY")
        team_id = request.GET.get("team_id")
        puzzle_id = request.GET.get("puzzle_id")
        if(team_id and team_id != "None"):
            submissions = submissions.filter(team__pk=team_id)
        if(puzzle_id and puzzle_id != "None"):
            submissions = submissions.filter(puzzle__pk=puzzle_id)

    else:
        page_num = request.GET.get("page_num")
        team_id = request.GET.get("team_id")
        puzzle_id = request.GET.get("puzzle_id")
        hunt = Hunt.objects.get(is_current_hunt=True)
        submissions = Submission.objects.filter(puzzle__hunt=hunt).exclude(team__location="DUMMY")
        arg_string = ""
        if(team_id):
            team_id = int(team_id)
            submissions = submissions.filter(team__pk=team_id)
            arg_string = arg_string + ("&team_id=%s" % team_id)
        if(puzzle_id):
            puzzle_id = int(puzzle_id)
            submissions = submissions.filter(puzzle__pk=puzzle_id)
            arg_string = arg_string + ("&puzzle_id=%s" % puzzle_id)
        submissions = submissions.select_related('team', 'puzzle').order_by('-pk')
        pages = Paginator(submissions, 30)
        try:
            submissions = pages.page(page_num)
        except PageNotAnInteger:
            submissions = pages.page(1)
        except EmptyPage:
            submissions = pages.page(pages.num_pages)

    form = SubmissionForm()
    try:
        date_query = Submission.objects.latest('modified_date').modified_date
        last_date = date_query.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    except Submission.DoesNotExist:
        last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    submission_list = [render_to_string('queue_row.html', {'submission': submission},
                                        request=request)
                       for submission in submissions]

    if request.is_ajax() or request.method == 'POST':
        context = {'submission_list': submission_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))
    else:
        context = {'form': form, 'page_info': submissions, 'arg_string': arg_string,
                   'submission_list': submission_list, 'last_date': last_date, 'hunt': hunt,
                   'puzzle_id': puzzle_id, 'team_id': team_id}
        return render(request, 'queue.html', add_apps_to_context(context, request))


@staff_member_required
def progress(request):
    """
    A view to handle puzzle unlocks via POST, handle unlock/solve update requests via AJAX,
    and render the progress page. Rendering the progress page is extremely data intensive and so
    the view involves a good amount of pre-fetching.
    """

    if request.method == 'POST':
        if "action" in request.POST:
            if request.POST.get("action") == "unlock":
                form = UnlockForm(request.POST)
                if form.is_valid():
                    t = Team.objects.get(pk=form.cleaned_data['team_id'])
                    p = Puzzle.objects.get(puzzle_id=form.cleaned_data['puzzle_id'])
                    if(p not in t.unlocked.all()):
                        u = Unlock.objects.create(team=t, puzzle=p, time=timezone.now())
                        return HttpResponse(json.dumps(u.serialize_for_ajax()))
                    else:
                        return HttpResponse(status=200)
            if request.POST.get("action") == "unlock_all":
                p = Puzzle.objects.get(pk=request.POST.get('puzzle_id'))
                response = []
                for team in p.hunt.team_set.all():
                    if(p not in team.unlocked.all()):
                        u = Unlock.objects.create(team=team, puzzle=p, time=timezone.now())
                        response.append(u.serialize_for_ajax())
                return HttpResponse(json.dumps(response))
        return HttpResponse(status=400)

    elif request.is_ajax():
        update_info = []
        if not ("last_solve_pk" in request.GET and
                "last_unlock_pk" in request.GET and
                "last_submission_pk" in request.GET):
            return HttpResponse(status=404)
        results = []

        last_solve_pk = request.GET.get("last_solve_pk")
        solves = list(Solve.objects.filter(pk__gt=last_solve_pk))
        for i in range(len(solves)):
            results.append(solves[i].serialize_for_ajax())

        last_unlock_pk = request.GET.get("last_unlock_pk")
        unlocks = list(Unlock.objects.filter(pk__gt=last_unlock_pk))
        for i in range(len(unlocks)):
            results.append(unlocks[i].serialize_for_ajax())

        last_submission_pk = request.GET.get("last_submission_pk")
        submissions = list(Submission.objects.filter(pk__gt=last_submission_pk))
        for i in range(len(submissions)):
            if(not submissions[i].team.solved.filter(pk=submissions[i].puzzle.pk).exists()):
                results.append(submissions[i].serialize_for_ajax())

        if(len(results) > 0):
            try:
                last_solve_pk = Solve.objects.latest('id').id
            except Solve.DoesNotExist:
                last_solve_pk = 0
            try:
                last_unlock_pk = Unlock.objects.latest('id').id
            except Unlock.DoesNotExist:
                last_unlock_pk = 0
            try:
                last_submission_pk = Submission.objects.latest('id').id
            except Submission.DoesNotExist:
                last_submission_pk = 0
            update_info = [last_solve_pk, last_unlock_pk, last_submission_pk]
        response = json.dumps({'messages': results, 'update_info': update_info})
        return HttpResponse(response)

    else:
        curr_hunt = Hunt.objects.get(is_current_hunt=True)
        teams = curr_hunt.real_teams.all().order_by('team_name')
        puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
        # An array of solves, organized by team then by puzzle
        # This array is essentially the grid on the progress page
        # The structure is messy, it was built part by part as features were added
        sol_array = []
        for team in teams:
            # These are defined to reduce DB queries
            solved = team.solved.all()                            # puzzles
            unlocked = team.unlocked.all()                        # puzzles
            solves = team.solve_set.select_related('submission')  # solves
            unlocks = team.unlock_set.all()                       # unlocks
            submissions = team.submission_set.all()               # submissions

            # Basic team information for row headers
            # The last element ('cells') is an array of the row's data
            sol_array.append({'team': team, 'cells': []})
            # What goes in each cell (item in "cells") is based on puzzle status
            for puzzle in puzzles:
                # Solved => solve object and puzzle id
                if puzzle in solved:
                    solve_time = solves.get(puzzle=puzzle).submission.submission_time
                    sol_array[-1]['cells'].append([solve_time, puzzle.puzzle_id])
                # Unlocked => Identify as unlocked, puzzle id, and unlock time
                elif puzzle in unlocked:
                    unlock_time = unlocks.get(puzzle=puzzle).time
                    puzzle_submissions = submissions.filter(puzzle=puzzle)
                    if(puzzle_submissions.exists()):
                        last_sub_time = puzzle_submissions.latest('id').submission_time
                    else:
                        last_sub_time = None
                    sol_array[-1]['cells'].append(["unlocked", puzzle.puzzle_id,
                                                   unlock_time, last_sub_time])
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
        try:
            last_submission_pk = Submission.objects.latest('id').id
        except Submission.DoesNotExist:
            last_submission_pk = 0
        context = {'puzzle_list': puzzles, 'team_list': teams, 'sol_array': sol_array,
                   'last_unlock_pk': last_unlock_pk, 'last_solve_pk': last_solve_pk,
                   'last_submission_pk': last_submission_pk}
        return render(request, 'progress.html', add_apps_to_context(context, request))


@staff_member_required
def charts(request):
    """ A view to render the charts page. Mostly just collecting and organizing data """

    # Charts 1 and 2
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    puzzles = curr_hunt.puzzle_set.all().order_by('puzzle_number')
    puzzle_info_dict1 = []
    puzzle_info_dict2 = []
    for puzzle in puzzles:
        team_count = (curr_hunt.team_set.exclude(location="DUMMY")
                                        .exclude(location="off_campus")
                                        .count())
        unlocked_count = (puzzle.unlocked_for.exclude(location="DUMMY")
                                             .exclude(location="off_campus")
                                             .filter(hunt=curr_hunt)
                                             .count())
        solved_count = (puzzle.solved_for.exclude(location="DUMMY")
                                         .exclude(location="off_campus")
                                         .filter(hunt=curr_hunt)
                                         .count())
        submission_count = (puzzle.submission_set.exclude(team__location="DUMMY")
                                                 .exclude(team__location="off_campus")
                                                 .filter(puzzle__hunt=curr_hunt)
                                                 .count())
        puzzle_info_dict1.append({
            "name": puzzle.puzzle_name,
            "locked": team_count - unlocked_count,
            "unlocked": unlocked_count - solved_count,
            "solved": solved_count
        })

        puzzle_info_dict2.append({
            "name": puzzle.puzzle_name,
            "incorrect": submission_count - solved_count,
            "correct": solved_count
        })

    # Chart 3
    time_zone = tz.gettz(settings.TIME_ZONE)
    subs = Submission.objects.filter(puzzle__hunt=curr_hunt).all().order_by("submission_time")
    grouped = itertools.groupby(subs, lambda x: x.submission_time.astimezone(time_zone)
                                                                 .strftime("%x - %H:00"))
    submission_hours = []
    for group, matches in grouped:
        matches = list(matches)
        amount = len(matches)
        # TODO: change this to be based on hunt date
        if(matches[0].puzzle.hunt.start_date < matches[0].submission_time and
           matches[0].submission_time < matches[0].puzzle.hunt.end_date):
            submission_hours.append({"hour": group, "amount": amount})

    # Chart 4
    solves = (Solve.objects.filter(puzzle__hunt=curr_hunt).all()
                           .order_by("submission__submission_time"))
    grouped = itertools.groupby(solves, lambda x: x.submission.submission_time
                                                              .astimezone(time_zone)
                                                              .strftime("%x - %H:00"))
    solve_hours = []
    for group, matches in grouped:
        matches = list(matches)
        amount = len(matches)
        if(matches[0].puzzle.hunt.start_date < matches[0].submission.submission_time and
           matches[0].submission.submission_time < matches[0].puzzle.hunt.end_date):
            solve_hours.append({"hour": group, "amount": amount})

    # Chart 5
    solves = solves.order_by("submission__submission_time")
    teams = list(curr_hunt.team_set.exclude(location="DUMMY").exclude(location="off_campus"))
    num_puzzles = puzzles.count()
    solve_points = []
    tmp = [None]
    for team in teams:
        tmp.append(0)
    for solve in solves:
        tmp[0] = solve.submission.submission_time
        if(solve.team in teams):
            tmp[teams.index(solve.team) + 1] += 1
            solve_points.append(tmp[:])

    # Info Table
    table_dict = {}
    for puzzle in puzzles:
        try:
            solve_set = (puzzle.solve_set.exclude(team__location="DUMMY")
                                         .exclude(team__location="off_campus"))
            solve = solve_set.order_by("submission__submission_time")[:1].get()
            table_dict[puzzle.puzzle_name] = {'first_team': solve.team.team_name,
                                              'first_time': solve.submission.submission_time,
                                              'num_solves': solve_set.count()}
        except Solve.DoesNotExist:
            max_time = datetime.max.replace(tzinfo=tz.gettz('UTC'))
            table_dict[puzzle.puzzle_name] = {'first_team': None,
                                              'first_time': max_time,
                                              'num_solves': puzzle.solve_set.count()}

    context = {'data1_list': puzzle_info_dict1, 'data2_list': puzzle_info_dict2,
               'data3_list': submission_hours, 'data4_list': solve_hours,
               'data5_list': solve_points, 'teams': teams, 'num_puzzles': num_puzzles,
               'table_dict': sorted(iter(table_dict.items()), key=lambda x: x[1]['first_time'])}
    return render(request, 'charts.html', add_apps_to_context(context, request))


@staff_member_required
def admin_chat(request):
    """
    A view to handle chat update requests via AJAX and render the staff chat
    page. Chat messages are pre-rendered for both standard and AJAX requests.
    """

    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    if request.method == 'POST':
        # We can trust all post parameters because user is already authenticated as staff
        if(request.POST.get('team_pk') == ""):
            return HttpResponse(status=400)
        if(request.POST.get("is_announcement") == "true"):
            messages = []
            for team in curr_hunt.real_teams.all():
                m = Message.objects.create(time=timezone.now(),
                                           text="[Announcement] " + request.POST.get('message'),
                                           is_response=(request.POST.get('is_response') == "true"),
                                           team=team)
                messages.append(m)
        else:
            team = Team.objects.get(pk=request.POST.get('team_pk'))
            m = Message.objects.create(time=timezone.now(), text=request.POST.get('message'),
                                       is_response=(request.POST.get('is_response') == "true"),
                                       team=team)
            team.last_received_message = m.pk
            team.save()
            messages = [m]

    else:
        if request.is_ajax():
            messages = Message.objects.filter(pk__gt=request.GET.get("last_pk"))
        else:
            messages = Message.objects.filter(team__hunt=curr_hunt)
        messages = messages.order_by('team', 'time').select_related('team')

    # This block assumes messages are grouped by team
    team_name = ""
    message_dict = {}
    for message in messages:
        if message.team.team_name != team_name:
            team_name = message.team.team_name
            message_dict[team_name] = {'pk': message.team.pk, 'messages': []}
        message_dict[team_name]['messages'].append(message)
    for team in message_dict:
        message_dict[team]['messages'] = render_to_string(
            'chat_messages.html', {'messages': message_dict[team]['messages'], 'team_name': team})

    try:
        last_pk = Message.objects.latest('id').id
    except Message.DoesNotExist:
        last_pk = 0

    context = {'message_dict': message_dict, 'last_pk': last_pk}
    if request.is_ajax() or request.method == 'POST':
        return HttpResponse(json.dumps(context))
    else:
        teams = curr_hunt.team_set.order_by("team_name").all()
        context['teams'] = teams
        return render(request, 'staff_chat.html', add_apps_to_context(context, request))


@staff_member_required
def hunt_management(request):
    """ A view to render the hunt management page """

    hunts = Hunt.objects.all()
    prepuzzles = Prepuzzle.objects.all()
    context = {'hunts': hunts, 'prepuzzles': prepuzzles}
    return render(request, 'hunt_management.html', add_apps_to_context(context, request))


@staff_member_required
def hunt_info(request):
    """ A view to render the hunt info page, which contains room and allergy information """

    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    if request.method == 'POST':
        if "json_data" in request.POST:
            team_data = json.loads(request.POST.get("json_data"))
            for pair in team_data:
                try:
                    team = Team.objects.get(id=pair['id'])
                    if(team.hunt == curr_hunt):
                        team.location = pair["location"]
                        team.save()
                except ObjectDoesNotExist:
                    return HttpResponse('bad data')
        return HttpResponse('teams updated!')
    else:
        teams = curr_hunt.real_teams
        people = []
        new_people = []
        for team in teams:
            people = people + list(team.person_set.all())
        try:
            old_hunt = Hunt.objects.get(hunt_number=curr_hunt.hunt_number - 1)
            new_people = [p for p in people if p.user.date_joined > old_hunt.start_date]
        except Hunt.DoesNotExist:
            new_people = people

        need_teams = teams.filter(location="need_a_room") | teams.filter(location="needs_a_room")
        have_teams = (teams.exclude(location="need_a_room")
                           .exclude(location="needs_a_room")
                           .exclude(location="off_campus"))
        offsite_teams = teams.filter(location="off_campus")

        context = {'curr_hunt': curr_hunt,
                   'people': people,
                   'new_people': new_people,
                   'need_teams': need_teams.order_by('id').all(),
                   'have_teams': have_teams.all(),
                   'offsite_teams': offsite_teams.all(),
                   }
        return render(request, 'staff_hunt_info.html', add_apps_to_context(context, request))


@staff_member_required
def control(request):
    """
    A view to handle all of the different management actions from staff users via POST requests.
    This view is not responsible for rendering any normal pages.
    """

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
                team.num_available_hints = 0
                team.save()
            return redirect('huntserver:hunt_management')

        if(request.POST["action"] == "getpuzzles"):
            if("puzzle_number" in request.POST and request.POST["puzzle_number"]):
                puzzles = Puzzle.objects.filter(puzzle_id=int(request.POST["puzzle_id"]))
                for puzzle in puzzles:
                    download_puzzle(puzzle)

            elif("hunt_number" in request.POST and request.POST["hunt_number"]):
                hunt = Hunt.objects.get(hunt_number=int(request.POST["hunt_number"]))
                for puzzle in hunt.puzzle_set.all():
                    download_puzzle(puzzle)

            return redirect('huntserver:hunt_management')

        if(request.POST["action"] == "getprepuzzle"):
            if("puzzle_number" in request.POST and request.POST["puzzle_number"]):
                puzzle = Prepuzzle.objects.get(pk=int(request.POST["puzzle_number"]))
                directory = settings.MEDIA_ROOT + "prepuzzles"
                download_zip(directory, str(puzzle.pk), puzzle.resource_link)

            return redirect('huntserver:hunt_management')

        if(request.POST["action"] == "gethunt"):
            if("hunt_number" in request.POST and request.POST["hunt_number"]):
                hunt = Hunt.objects.get(hunt_number=int(request.POST["hunt_number"]))
                directory = settings.MEDIA_ROOT + "hunt"
                download_zip(directory, str(hunt.hunt_number), hunt.resource_link)

            return redirect('huntserver:hunt_management')

        if(request.POST["action"] == "new_current_hunt"):
            new_curr = Hunt.objects.get(hunt_number=int(request.POST.get('hunt_number')))
            new_curr.is_current_hunt = True
            new_curr.save()
            return redirect('huntserver:hunt_management')

        else:
            return HttpResponseNotFound('access denied')


@staff_member_required
def staff_hints_text(request):
    """
    A view to handle hint response updates via POST, handle hint request update requests via AJAX,
    and render the hint page. Hints are pre-rendered for standard and AJAX requests.
    """

    if request.method == 'POST':
        form = HintResponseForm(request.POST)
        if not form.is_valid():
            return HttpResponse(status=400)
        h = Hint.objects.get(pk=form.cleaned_data['hint_id'])
        h.response = form.cleaned_data['response']
        h.response_time = timezone.now()
        h.last_modified_time = timezone.now()
        h.save()
        hints = [h]

    elif request.is_ajax():
        last_date = datetime.strptime(request.GET.get("last_date"), '%Y-%m-%dT%H:%M:%S.%fZ')
        last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
        hints = Hint.objects.filter(last_modified_time__gt=last_date)

    else:
        page_num = request.GET.get("page_num")
        hunt = Hunt.objects.get(is_current_hunt=True)
        hints = Hint.objects.filter(puzzle__hunt=hunt)
        hints = hints.select_related('team', 'puzzle').order_by('-pk')
        pages = Paginator(hints, 10)
        try:
            hints = pages.page(page_num)
        except PageNotAnInteger:
            hints = pages.page(1)
        except EmptyPage:
            hints = pages.page(pages.num_pages)

    try:
        time_query = Hint.objects.latest('last_modified_time').last_modified_time
        last_date = time_query.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    except Hint.DoesNotExist:
        last_date = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    hint_list = []
    for hint in hints:
        form = HintResponseForm(initial={"response": hint.response, "hint_id": hint.pk})
        hint_list.append(render_to_string('hint_row.html', {'hint': hint, "response_form": form},
                                          request=request))

    if request.is_ajax() or request.method == 'POST':
        context = {'hint_list': hint_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))
    else:
        context = {'page_info': hints, 'hint_list': hint_list,
                   'last_date': last_date, 'hunt': hunt}
        return render(request, 'staff_hints.html', add_apps_to_context(context, request))


@staff_member_required
def staff_hints_control(request):
    """
    A view to handle the incrementing, decrementing, and updating the team hint counts on
    the hints staff page.
    """

    if request.is_ajax():
        if("action" in request.POST and "value" in request.POST and "team_pk" in request.POST):
            if(request.POST.get("action") == "update"):
                try:
                    update_value = int(request.POST.get("value"))
                    team_pk = int(request.POST.get("team_pk"))
                    team = Team.objects.get(pk=team_pk)
                    if(team.num_available_hints + update_value >= 0):
                        team.num_available_hints = F('num_available_hints') + update_value
                        team.save()

                except ValueError:
                    pass  # Maybe a 4XX or 5XX in the future
    else:
        return HttpResponse("Incorrect usage of hint control page")

    hunt = Hunt.objects.get(is_current_hunt=True)
    return HttpResponse(json.dumps(list(hunt.team_set.values_list('pk', 'num_available_hints'))))


@staff_member_required
def emails(request):
    """
    A view to send emails out to hunt participants upon recieveing a valid post request as well as
    rendering the staff email form page
    """

    teams = Hunt.objects.get(is_current_hunt=True).real_teams
    people = []
    for team in teams:
        people = people + list(team.person_set.all())
    email_list = [person.user.email for person in people]

    if request.method == 'POST':
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            subject = email_form.cleaned_data['subject']
            message = email_form.cleaned_data['message']
            email_to_chunks = [email_list[x: x + 80] for x in range(0, len(email_list), 80)]
            for to_chunk in email_to_chunks:
                email = EmailMessage(subject, message, 'puzzlehuntcmu@gmail.com',
                     [], to_chunk)
                email.send()
            return HttpResponseRedirect('')
    else:
        email_form = EmailForm()
    context = {'email_list': (', ').join(email_list), 'email_form': email_form}
    return render(request, 'email.html', add_apps_to_context(context, request))
