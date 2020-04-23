from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.shortcuts import render
from django.contrib import messages
import random
import re

from .models import Hunt, Team
from .forms import PersonForm, ShibUserForm

import logging
logger = logging.getLogger(__name__)


def index(request):
    """ Main landing page view, mostly static with the exception of hunt info """
    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    team = curr_hunt.team_from_user(request.user)
    return render(request, "index.html", {'curr_hunt': curr_hunt, 'team': team})


def previous_hunts(request):
    """ A view to render the list of previous hunts, will show any hunt that is 'public' """
    old_hunts = []
    for hunt in Hunt.objects.all().order_by("hunt_number"):
        if(hunt.is_public):
            old_hunts.append(hunt)
    return render(request, "previous_hunts.html", {'hunts': old_hunts})


def registration(request):
    """
    The view that handles team registration. Mostly deals with creating the team object from the
    post request. The rendered page is nearly entirely static.
    """

    curr_hunt = Hunt.objects.get(is_current_hunt=True)
    team = curr_hunt.team_from_user(request.user)
    if(request.method == 'POST' and "form_type" in request.POST):
        if(request.POST["form_type"] == "new_team" and team is None):
            if(curr_hunt.team_set.filter(team_name__iexact=request.POST.get("team_name")).exists()):
                messages.error(request, "The team name you have provided already exists.")
            elif(re.match(".*[A-Za-z0-9].*", request.POST.get("team_name"))):
                join_code = ''.join(random.choice("ACDEFGHJKMNPRSTUVWXYZ2345679") for _ in range(5))
                team = Team.objects.create(team_name=request.POST.get("team_name"), hunt=curr_hunt,
                                           location=request.POST.get("need_room"),
                                           join_code=join_code)
                request.user.person.teams.add(team)
                logger.info("User %s created team %s" % (str(request.user), str(team)))
            else:
                messages.error(request,
                               "Your team name must contain at least one alphanumeric character.")
        elif(request.POST["form_type"] == "join_team" and team is None):
            team = curr_hunt.team_set.get(team_name=request.POST.get("team_name"))
            if(len(team.person_set.all()) >= team.hunt.team_size):
                messages.error(request, "The team you have tried to join is already full.")
                team = None
            elif(team.join_code.lower() != request.POST.get("join_code").lower()):
                messages.error(request, "The team join code you have entered is incorrect.")
                team = None
            else:
                request.user.person.teams.add(team)
                logger.info("User %s joined team %s" % (str(request.user), str(team)))
        elif(request.POST["form_type"] == "leave_team"):
            request.user.person.teams.remove(team)
            logger.info("User %s left team %s" % (str(request.user), str(team)))
            if(team.person_set.count() == 0 and team.hunt.is_locked):
                logger.info("Team %s was deleted because it was empty." % (str(team)))
                team.delete()
            team = None
            messages.success(request, "You have successfully left the team.")
        elif(request.POST["form_type"] == "new_location" and team is not None):
            old_location = team.location
            team.location = request.POST.get("team_location")
            team.save()
            logger.info("User %s changed the location for team %s from %s to %s" %
                        (str(request.user), str(team.team_name), old_location, team.location))
            messages.success(request, "Location successfully updated")
        elif(request.POST["form_type"] == "new_name" and team is not None and
                not team.hunt.in_reg_lockdown):
            if(curr_hunt.team_set.filter(team_name__iexact=request.POST.get("team_name")).exists()):
                messages.error(request, "The team name you have provided already exists.")
            else:
                old_name = team.team_name
                team.team_name = request.POST.get("team_name")
                team.save()
                logger.info("User %s renamed team %s to %s" %
                            (str(request.user), old_name, team.team_name))
                messages.success(request, "Team name successfully updated")

    if(team is not None):
        return render(request, "registration.html",
                      {'registered_team': team, 'curr_hunt': curr_hunt})
    else:
        teams = curr_hunt.real_teams.order_by(Lower('team_name'))
        return render(request, "registration.html",
                      {'teams': teams, 'curr_hunt': curr_hunt})


@login_required
def user_profile(request):
    """ A view to handle user information update POST data and render the user information form. """

    if request.method == 'POST':
        uf = ShibUserForm(request.POST, instance=request.user)
        pf = PersonForm(request.POST, instance=request.user.person)
        if uf.is_valid() and pf.is_valid():
            uf.save()
            pf.save()
            messages.success(request, "User information successfully updated.")
        else:
            context = {'user_form': uf, 'person_form': pf}
            return render(request, "user_profile.html", context)
    user_form = ShibUserForm(instance=request.user)
    person_form = PersonForm(instance=request.user.person)
    context = {'user_form': user_form, 'person_form': person_form}
    return render(request, "user_profile.html", context)
