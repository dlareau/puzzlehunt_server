from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
import random
import re

from .utils import team_from_user_hunt
from .models import Hunt, Team
from .forms import UserForm, PersonForm, ShibUserForm

def index(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    return render(request, "index.html", {'curr_hunt': curr_hunt})

def current_hunt_info(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    return render(request, "hunt_info.html", {'curr_hunt': curr_hunt})

def previous_hunts(request):
    old_hunts = []
    for hunt in Hunt.objects.all().order_by("hunt_number"):
        if(hunt.is_public):
            old_hunts.append(hunt)
    return render(request, "previous_hunts.html", {'hunts': old_hunts})

def registration(request):
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    team = team_from_user_hunt(request.user, curr_hunt)
    error = ""
    if(request.method == 'POST' and "form_type" in request.POST):
        if(request.POST["form_type"] == "new_team"):
            if(curr_hunt.team_set.filter(team_name__iexact=request.POST.get("team_name")).exists()):
                error = "The team name you have provided already exists."
            elif(re.match(".*[A-Za-z0-9].*", request.POST.get("team_name"))):
                join_code = ''.join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(5))
                team = Team.objects.create(team_name=request.POST.get("team_name"), hunt=curr_hunt, 
                                           location=request.POST.get("need_room"), join_code=join_code)
                request.user.person.teams.add(team)
            else:
                error = "Your team name must contain at least one alphanumeric character."
        elif(request.POST["form_type"] == "join_team"):
            team = curr_hunt.team_set.get(team_name=request.POST.get("team_name"))
            if(len(team.person_set.all()) >= team.hunt.team_size):
                error = "The team you have tried to join is already full."
                team = None
            elif(team.join_code.lower() != request.POST.get("join_code").lower()):
                error = "The team join code you have entered is incorrect."
                team = None
            else:
                request.user.person.teams.add(team)
        elif(request.POST["form_type"] == "leave_team"):
            request.user.person.teams.remove(team)
            team = None

    if(team != None):
        return render(request, "registration.html", {'registered_team': team})
    else:
        teams = curr_hunt.real_teams
        return render(request, "registration.html", {'teams': teams, 'error': error})

@login_required
def user_profile(request):
    # For form submission
    if request.method == 'POST':
        uf = ShibUserForm(request.POST, instance=request.user)
        pf = PersonForm(request.POST, instance=request.user.person)
        if uf.is_valid() and pf.is_valid():
            uf.save()
            pf.save()
        else:
            context = {'user_form': uf, 'person_form': pf}
            return render(request, "user_profile.html", context)
    user_form = ShibUserForm(instance=request.user)
    person_form = PersonForm(instance=request.user.person)
    context = {'user_form': user_form, 'person_form': person_form}
    return render(request, "user_profile.html", context)