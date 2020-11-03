from datetime import datetime
from dateutil import tz
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib import messages
from django.db.models import F, Max, Count, Min, Subquery, OuterRef
from django.db.models.fields import PositiveIntegerField
from django.db.models.functions import Lower
from huey.contrib.djhuey import result
import json
from copy import deepcopy
# from silk.profiling.profiler import silk_profile

from .models import Submission, Hunt, Team, Puzzle, Unlock, Solve, Message, Prepuzzle, Hint, Person
from .forms import SubmissionForm, UnlockForm, EmailForm, HintResponseForm, LookupForm

DT_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


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
        s.update_response(response)
        submissions = [s]

    elif request.is_ajax():
        last_date = datetime.strptime(request.GET.get("last_date"), DT_FORMAT)
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
        last_date = Submission.objects.latest('modified_date').modified_date.strftime(DT_FORMAT)
    except Submission.DoesNotExist:
        last_date = timezone.now().strftime(DT_FORMAT)
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
        solves = Solve.objects.filter(pk__gt=last_solve_pk)
        for solve in solves:
            results.append(solve.serialize_for_ajax())

        last_unlock_pk = request.GET.get("last_unlock_pk")
        unlocks = Unlock.objects.filter(pk__gt=last_unlock_pk)
        for unlock in unlocks:
            results.append(unlock.serialize_for_ajax())

        last_submission_pk = request.GET.get("last_submission_pk")
        submissions = Submission.objects.filter(pk__gt=last_submission_pk)
        for submission in submissions:
            if(not submission.team.solved.filter(pk=submission.puzzle.pk).exists()):
                results.append(submission.serialize_for_ajax())

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

        sol_dict = {}
        puzzle_dict = {}
        for puzzle in puzzles:
            puzzle_dict[puzzle.pk] = ['locked', puzzle.puzzle_id]
        for team in teams:
            sol_dict[team.pk] = deepcopy(puzzle_dict)

        data = Unlock.objects.filter(team__hunt=curr_hunt).exclude(team__location='DUMMY')
        data = data.values_list('team', 'puzzle').annotate(Max('time'))

        for point in data:
            sol_dict[point[0]][point[1]] = ['unlocked', point[2]]

        data = Submission.objects.filter(team__hunt=curr_hunt).exclude(team__location='DUMMY')
        data = data.values_list('team', 'puzzle').annotate(Max('submission_time'))
        data = data.annotate(Count('solve'))

        for point in data:
            if(point[3] == 0):
                sol_dict[point[0]][point[1]].append(point[2])
            else:
                sol_dict[point[0]][point[1]] = ['solved', point[2]]
        sol_list = []
        for team in teams:
            puzzle_list = [[puzzle.puzzle_id] + sol_dict[team.pk][puzzle.pk] for puzzle in puzzles]
            sol_list.append({'team': {'name': team.team_name, 'pk': team.pk},
                             'puzzles': puzzle_list})

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
        context = {'puzzle_list': puzzles, 'team_list': teams, 'sol_list': sol_list,
                   'last_unlock_pk': last_unlock_pk, 'last_solve_pk': last_solve_pk,
                   'last_submission_pk': last_submission_pk}
        return render(request, 'progress.html', add_apps_to_context(context, request))


@staff_member_required
def charts(request):
    """ A view to render the charts page. Mostly just collecting and organizing data """

    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    puzzles = curr_hunt.puzzle_set.order_by('puzzle_number')
    teams = curr_hunt.real_teams.exclude(location="DUMMY")
    num_teams = teams.count()
    num_puzzles = puzzles.count()

    names = puzzles.values_list('puzzle_name', flat=True)

    # Charts 1, 2 and 7
    puzzle_info_dict1 = []
    puzzle_info_dict2 = []
    puzzle_info_dict7 = []

    solves = puzzles.annotate(solved=Count('solve')).values_list('solved', flat=True)
    subs = puzzles.annotate(subs=Count('submission')).values_list('subs', flat=True)
    unlocks = puzzles.annotate(unlocked=Count('unlock')).values_list('unlocked', flat=True)
    hints = puzzles.annotate(hints=Count('hint')).values_list('hints', flat=True)
    puzzle_data = zip(names, solves, subs, unlocks, hints)
    for puzzle in puzzle_data:
        puzzle_info_dict1.append({
            "name": puzzle[0],
            "locked": num_teams - puzzle[3],
            "unlocked": puzzle[3] - puzzle[1],
            "solved": puzzle[1]
        })

        puzzle_info_dict2.append({
            "name": puzzle[0],
            "incorrect": puzzle[2] - puzzle[1],
            "correct": puzzle[1]
        })

        puzzle_info_dict7.append({
            "name": puzzle[0],
            "hints": puzzle[4]
        })

    # Chart 3
    submission_hours = []
    subs = Submission.objects.filter(puzzle__hunt=curr_hunt,
                                     submission_time__gte=curr_hunt.start_date,
                                     submission_time__lte=curr_hunt.end_date)
    subs = subs.values_list('submission_time__year',
                            'submission_time__month',
                            'submission_time__day',
                            'submission_time__hour')
    subs = subs.annotate(Count("id")).order_by('submission_time__year',
                                               'submission_time__month',
                                               'submission_time__day',
                                               'submission_time__hour')
    for sub in subs:
        time_string = "%02d/%02d/%04d - %02d:00" % (sub[1], sub[2], sub[0], sub[3])
        submission_hours.append({"hour": time_string, "amount": sub[4]})

    # Chart 4
    solve_hours = []
    solves = Solve.objects.filter(puzzle__hunt=curr_hunt,
                                  submission__submission_time__gte=curr_hunt.start_date,
                                  submission__submission_time__lte=curr_hunt.end_date)
    solves = solves.values_list('submission__submission_time__year',
                                'submission__submission_time__month',
                                'submission__submission_time__day',
                                'submission__submission_time__hour')
    solves = solves.annotate(Count("id")).order_by('submission__submission_time__year',
                                                   'submission__submission_time__month',
                                                   'submission__submission_time__day',
                                                   'submission__submission_time__hour')
    for solve in solves:
        time_string = "%02d/%02d/%04d - %02d:00" % (solve[1], solve[2], solve[0], solve[3])
        solve_hours.append({"hour": time_string, "amount": solve[4]})

    # Chart 5
    solve_points = []
    # solves = Solve.objects.filter(puzzle__hunt=curr_hunt,
    #                               submission__submission_time__gte=curr_hunt.start_date,
    #                               submission__submission_time__lte=curr_hunt.end_date)
    # solves = solves.order_by('submission__submission_time')

    # team_dict = {}
    # for team in teams:
    #     team_dict[team] = 0
    # progress = [0] * (num_puzzles + 1)
    # progress[0] = num_teams
    # solve_points.append([curr_hunt.start_date] + progress[::-1])
    # for solve in solves:
    #     progress[team_dict[solve.team]] -= 1
    #     team_dict[solve.team] += 1
    #     progress[team_dict[solve.team]] += 1
    #     solve_points.append([solve.submission.submission_time] + progress[::-1])

    # for puzzle in puzzles:
    #     points = puzzle.solve_set.order_by('submission__submission_time')
    #     points = points.values_list('submission__submission_time', flat=True)
    #     points = zip([curr_hunt.start_date] + list(points), range(len(points) + 1))
    #     solve_points.append({'puzzle': puzzle, 'points': points})

    # for team in teams:
    #     points = team.solve_set.order_by('submission__submission_time')
    #     points = points.values_list('submission__submission_time', flat=True)
    #     points = zip([curr_hunt.start_date] + list(points), range(len(points) + 1))
    #     solve_points.append({'team': team, 'points': points})

    # Chart 6
    solve_time_data = []
    # sq1 = Unlock.objects.filter(puzzle=OuterRef('puzzle'), team=OuterRef('team'))
    # sq1 = sq1.values('time')[:1]
    # sq2 = Solve.objects.filter(pk=OuterRef('pk')).values('submission__submission_time')[:1]
    # solves = Solve.objects.filter(puzzle__hunt=curr_hunt,
    #                               submission__submission_time__gte=curr_hunt.start_date,
    #                               submission__submission_time__lte=curr_hunt.end_date)
    # solves = solves.annotate(t1=Subquery(sq1), t2=Subquery(sq2))
    # solves = solves.annotate(solve_duration=F('t2') - F('t1'))
    # std = solves.values_list('puzzle__puzzle_number', 'solve_duration')
    # solve_time_data = [(x[0]+(random.random()/2)-0.5, x[1].total_seconds()/60) for x in std]

    # Info Table
    # with silk_profile(name="Info Table"):
    solves = Solve.objects.filter(team__hunt=curr_hunt)
    mins = solves.values_list('puzzle').annotate(m=Min('id')).values_list('m', flat=True)
    results = Solve.objects.filter(pk__in=mins).values_list('puzzle__puzzle_id',
                                                            'puzzle__puzzle_name',
                                                            'team__team_name',
                                                            'submission__submission_time')
    results = list(results.annotate(Count('puzzle__solve')).order_by('puzzle__puzzle_id'))

    context = {'data1_list': puzzle_info_dict1, 'data2_list': puzzle_info_dict2,
               'data3_list': submission_hours, 'data4_list': solve_hours,
               'data5_list': solve_points, 'teams': teams, 'num_puzzles': num_puzzles,
               'chart_rows': results, 'puzzles': puzzles, 'data6_list': solve_time_data,
               'data7_list': puzzle_info_dict7}
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
            team.num_waiting_messages = team.num_waiting_messages + 1
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
        teams = curr_hunt.team_set.order_by(Lower("team_name")).all()
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
        people = Person.objects.filter(teams__hunt=curr_hunt)
        try:
            old_hunt = Hunt.objects.get(hunt_number=curr_hunt.hunt_number - 1)
            new_people = people.filter(user__date_joined__gt=old_hunt.end_date)
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
    if(request.method == 'GET' and "action" in request.GET):
        if(request.GET['action'] == "check_task"):
            task_result = result(request.GET['task_id'])
            if(task_result is None):
                response = {"have_result": False, "result_text": ""}
            else:
                response = {"have_result": True, "result_text": task_result}
            return HttpResponse(json.dumps(response))

    if(request.method == 'POST' and "action" in request.POST):
        if(request.POST["action"] == "initial"):
            if(curr_hunt.is_open):
                teams = curr_hunt.team_set.all().order_by('team_name')
            else:
                teams = curr_hunt.team_set.filter(playtester=True).order_by('team_name')
            for team in teams:
                team.unlock_puzzles()
            messages.success(request, "Initial puzzles released")
            return redirect('huntserver:hunt_management')
        if(request.POST["action"] == "reset"):
            teams = curr_hunt.team_set.all().order_by('team_name')
            for team in teams:
                team.reset()
            messages.success(request, "Progress reset")
            return redirect('huntserver:hunt_management')

        if(request.POST["action"] == "new_current_hunt"):
            new_curr = Hunt.objects.get(hunt_number=int(request.POST.get('hunt_number')))
            new_curr.is_current_hunt = True
            new_curr.save()
            messages.success(request, "Set new current hunt")
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
    else:
        team_id = request.GET.get("team_id")
        hint_status = request.GET.get("hint_status")
        puzzle_id = request.GET.get("puzzle_id")
        hunt = Hunt.objects.get(is_current_hunt=True)
        hints = Hint.objects.filter(puzzle__hunt=hunt)
        arg_string = ""
        if(team_id):
            team_id = int(team_id)
            hints = hints.filter(team__pk=team_id)
            arg_string = arg_string + ("&team_id=%s" % team_id)
        if(puzzle_id):
            puzzle_id = int(puzzle_id)
            hints = hints.filter(puzzle__pk=puzzle_id)
            arg_string = arg_string + ("&puzzle_id=%s" % puzzle_id)
        if(hint_status):
            if(hint_status == "answered"):
                hints = hints.exclude(response="")
            elif(hint_status == "unanswered"):
                hints = hints.filter(response="")
            arg_string = arg_string + ("&hint_status=%s" % hint_status)
        if(request.is_ajax()):
            last_date = datetime.strptime(request.GET.get("last_date"), DT_FORMAT)
            last_date = last_date.replace(tzinfo=tz.gettz('UTC'))
            hints = hints.filter(last_modified_time__gt=last_date)
        else:  # Normal get request
            page_num = request.GET.get("page_num")
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
        last_date = time_query.strftime(DT_FORMAT)
    except Hint.DoesNotExist:
        last_date = timezone.now().strftime(DT_FORMAT)

    hint_list = []
    for hint in hints:
        hint_list.append(render_to_string('hint_row.html', {'hint': hint, 'staff_side': True},
                                          request=request))

    if request.is_ajax() or request.method == 'POST':
        context = {'hint_list': hint_list, 'last_date': last_date}
        return HttpResponse(json.dumps(context))
    else:
        form = HintResponseForm()
        context = {'page_info': hints, 'hint_list': hint_list,  'arg_string': arg_string,
                   'last_date': last_date, 'hunt': hunt, 'puzzle_id': puzzle_id, 'team_id': team_id,
                   'hint_status': hint_status, "response_form": form}
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
    A view to send emails out to hunt participants upon receiving a valid post request as well as
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
                email = EmailMessage(subject, message, 'puzzlehuntcmu@gmail.com', [], to_chunk)
                email.send()
            return HttpResponseRedirect('')
    else:
        email_form = EmailForm()
    context = {'email_list': (', ').join(email_list), 'email_form': email_form}
    return render(request, 'email.html', add_apps_to_context(context, request))


@staff_member_required
def lookup(request):
    """
    A view to search for users/teams
    """
    person = None
    team = None
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    if request.method == 'POST':
        lookup_form = LookupForm(request.POST)
        if lookup_form.is_valid():
            search_string = lookup_form.cleaned_data['search_string']
            results = {'teams': Team.objects.search(search_string),
                       'people': Person.objects.search(search_string)}
    else:
        if("person_pk" in request.GET):
            person = Person.objects.get(pk=request.GET.get("person_pk"))
        if("team_pk" in request.GET):
            team = Team.objects.get(pk=request.GET.get("team_pk"))
            team.latest_submissions = team.submission_set.values_list('puzzle')
            team.latest_submissions = team.latest_submissions.annotate(Max('submission_time'))
            sq1 = Solve.objects.filter(team__pk=OuterRef('pk'), puzzle__is_meta=True).order_by()
            sq1 = sq1.values('team').annotate(c=Count('*')).values('c')
            sq1 = Subquery(sq1, output_field=PositiveIntegerField())
            all_teams = team.hunt.team_set.annotate(metas=sq1, solves=Count('solved'))
            all_teams = all_teams.annotate(last_time=Max('solve__submission__submission_time'))
            ids = all_teams.order_by(F('metas').desc(nulls_last=True),
                                     F('solves').desc(nulls_last=True),
                                     F('last_time').asc(nulls_last=True))
            team.rank = list(ids.values_list('pk', flat=True)).index(team.pk) + 1

        lookup_form = LookupForm()
        results = {}
    context = {'lookup_form': lookup_form, 'results': results, 'person': person, 'team': team,
               'curr_hunt': curr_hunt}
    return render(request, 'lookup.html', add_apps_to_context(context, request))
