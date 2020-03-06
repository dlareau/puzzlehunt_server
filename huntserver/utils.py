from django.conf import settings
from django.db.models import F
from django.utils import timezone
from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from subprocess import call, STDOUT
import os
from django.core.cache import cache

from .models import Hunt, HintUnlockPlan


import logging
logger = logging.getLogger(__name__)


def download_zip(directory, filename, url):
    if(url == ""):
        return

    logger.info("Attempting to download zip %s to %s/%s" % (url, directory, filename))

    if(not os.path.isdir(directory)):
        call(["mkdir", directory])

    file_str = directory + "/" + filename + ".zip"
    FNULL = open(os.devnull, 'w')
    command_str = "wget --max-redirect=20 {} -O {}".format(url, file_str)
    call(command_str, stdout=FNULL, stderr=STDOUT, shell=True)
    command_str = "unzip -o -d {}/{} {}".format(directory, filename, file_str)
    call(command_str, stdout=FNULL, stderr=STDOUT, shell=True)
    FNULL.close()


def download_pdf(directory, filename, url):
    if(url == ""):
        return

    logger.info("Attempting to download pdf %s to %s/%s" % (url, directory, filename))

    if(not os.path.isdir(directory)):
        call(["mkdir", directory])

    FNULL = open(os.devnull, 'w')
    file_str = directory + "/" + filename + ".pdf"
    command_str = "wget {} -O {}".format(url, file_str)
    call(command_str, stdout=FNULL, stderr=STDOUT, shell=True)
    FNULL.close()


def download_puzzle(puzzle):
    directory = settings.MEDIA_ROOT + "puzzles"

    download_pdf(directory, str(puzzle.puzzle_id), puzzle.link)
    download_zip(directory, str(puzzle.puzzle_id), puzzle.resource_link)
    download_pdf(settings.MEDIA_ROOT + "solutions", str(puzzle.puzzle_id) + "_sol",
                 puzzle.solution_link)


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


def check_puzzles(hunt, new_points, teams):
    if(new_points > 0):
        teams.update(num_unlock_points=F('num_unlock_points') + new_points)
        for team in teams:
            team.unlock_puzzles()


@db_periodic_task(crontab(minute='*/1'))
def update_time_items():
    try:
        hunt = Hunt.objects.get(is_current_hunt=True)
    except Hunt.DoesNotExist:
        return

    last_update_time = cache.get('last_update_time', timezone.now())
    last_update_time = last_update_time.replace(second=0, microsecond=0)
    cache.set(timezone.now(), 30 * 60)
    diff_time = timezone.now().replace(second=0, microsecond=0) - last_update_time
    diff_minutes = diff_time.seconds / 60

    if(hunt.is_open):
        check_hints(hunt)

    if(diff_minutes >= 1):
        new_points = hunt.points_per_minute * diff_minutes

        if(hunt.is_open):
            check_puzzles(hunt, new_points, hunt.team_set.all())
        else:
            playtesters = hunt.team_set.filter(playtester=True).all()
            playtesters = [t for t in playtesters if t.playtest_happening]
            if(len(playtesters) > 0):
                check_puzzles(hunt, new_points, playtesters)
