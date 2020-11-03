from django.conf import settings
from django.db.models import F
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from django.core.cache import cache

from .models import Hunt, HintUnlockPlan


import logging
logger = logging.getLogger(__name__)
wget_arguments = "--max-redirect=20 --show-progress --progress=bar:force:noscroll"


def parse_attributes(META):
    shib_attrs = {}
    error = False
    for header, attr in list(settings.SHIB_ATTRIBUTE_MAP.items()):
        required, name = attr
        values = META.get(header, None)
        if not values:
            values = META.get("HTTP_" + (header.replace("-", "_")).upper(), None)
        value = None
        if values:
            # If multiple attributes releases just care about the 1st one
            try:
                value = values.split(';')[0]
            except IndexError:
                value = values

        shib_attrs[name] = value
        if not value or value == '':
            if required:
                error = True
    return shib_attrs, error


def check_hints(hunt):
    num_min = (timezone.now() - hunt.start_date).seconds / 60
    for hup in hunt.hintunlockplan_set.exclude(unlock_type=HintUnlockPlan.SOLVES_UNLOCK):
        if((hup.unlock_type == hup.TIMED_UNLOCK and
           hup.num_triggered < 1 and num_min > hup.unlock_parameter) or
           (hup.unlock_type == hup.INTERVAL_UNLOCK and
           num_min / hup.unlock_parameter > hup.num_triggered)):
            hunt.team_set.all().update(num_available_hints=F('num_available_hints') + 1)
            hup.num_triggered = hup.num_triggered + 1
            hup.save()


def check_puzzles(hunt, new_points, teams, team_is_list=False):
    if(new_points > 0):
        if(team_is_list):
            for team in teams:
                team.num_unlock_points = team.num_unlock_points + new_points
                team.save()
        else:
            teams.update(num_unlock_points=F('num_unlock_points') + new_points)

        for team in teams:
            team.unlock_puzzles()


@db_periodic_task(crontab(minute='*/1'))
def update_time_items():
    try:
        hunt = Hunt.objects.get(is_current_hunt=True)
    except Hunt.DoesNotExist:
        return

    if(hunt.is_open):
        check_hints(hunt)

    last_update_time = cache.get('last_update_time')
    if(last_update_time is None):
        cache.set('last_update_time', timezone.now(), 30 * 60)
        last_update_time = timezone.now()

    last_update_time = last_update_time.replace(second=0, microsecond=0)
    diff_time = timezone.now().replace(second=0, microsecond=0) - last_update_time
    diff_minutes = diff_time.seconds / 60

    if(diff_minutes >= 1):
        cache.set('last_update_time', timezone.now(), 30 * 60)
        new_points = hunt.points_per_minute * diff_minutes

        if(hunt.is_open):
            check_puzzles(hunt, new_points, hunt.team_set.all())
        else:
            playtesters = hunt.team_set.filter(playtester=True).all()
            playtesters = [t for t in playtesters if t.playtest_happening]
            if(len(playtesters) > 0):
                check_puzzles(hunt, new_points, playtesters, True)
