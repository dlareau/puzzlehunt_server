from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Person, Team
from subprocess import call, STDOUT
import os
from PyPDF2 import PdfFileReader

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
    with open(file_str, "rb") as f:
        num_pages = PdfFileReader(f).getNumPages()
    command_str = "convert -density 200 {} {}/{}.png".format(file_str, directory, filename)
    call(command_str, stdout=FNULL, stderr=STDOUT, shell=True)
    FNULL.close()
    return num_pages


def download_puzzle(puzzle):
    directory = settings.MEDIA_ROOT + "puzzles"

    puzzle.num_pages = download_pdf(directory, str(puzzle.puzzle_id), puzzle.link)
    puzzle.save()

    download_zip(directory, str(puzzle.puzzle_id), puzzle.resource_link)
    download_pdf(settings.MEDIA_ROOT + "solutions", str(puzzle.puzzle_id) + "_sol",
                 puzzle.solution_link)


def parse_attributes(META):
    shib_attrs = {}
    error = False
    for header, attr in list(settings.SHIB_ATTRIBUTE_MAP.items()):
        required, name = attr
        values = META.get(header, None)
        value = None
        if values:
            # If multiple attributes releases just care about the 1st one
            try:
                value = values.split(';')[0]
            except:
                value = values

        shib_attrs[name] = value
        if not value or value == '':
            if required:
                error = True
    return shib_attrs, error


# Takes a hunt and returns the "dummy" team for that hunt, making it if needed
def dummy_team_from_hunt(hunt):
    try:
        team = Team.objects.get(hunt=hunt, location="DUMMY")
    except:
        team = Team.objects.create(team_name=hunt.hunt_name + "_DUMMY", hunt=hunt,
                    location="DUMMY", join_code="WRONG")
    return team


# Takes a user and a hunt and returns either the user's team for that hunt or None
def team_from_user_hunt(user, hunt):
    if(not user.is_authenticated):
        return None
    teams = get_object_or_404(Person, user=user).teams.filter(hunt=hunt)
    return teams[0] if (len(teams) > 0) else None
