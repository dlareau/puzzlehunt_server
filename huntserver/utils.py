from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from .models import Solve, Unlock, Person, Team
from django.utils import timezone
from subprocess import call
import os
from PyPDF2 import PdfFileReader
import re

import logging
logger = logging.getLogger(__name__)


# Automatic submission response system
# Takes a submission object and should return a string
# Returning an empty string means that huntstaff should respond via the queue
# Order of response importance: Correct regex, Correct default,
# Incorrect regex, Incorrect (archived), Staff response.
def respond_to_submission(submission):
    # Check against regexes
    regex_response = ""
    for resp in submission.puzzle.response_set.all():
        if(re.match(resp.regex, submission.submission_text, re.IGNORECASE)):
            regex_response = resp.text
            break
    # Compare against correct answer
    if(submission.puzzle.answer.lower() == submission.submission_text.lower()):
        # Make sure we don't have duplicate or after hunt submission objects
        if(not submission.puzzle.hunt.is_public):
            if(submission.puzzle not in submission.team.solved.all()):
                Solve.objects.create(puzzle=submission.puzzle,
                    team=submission.team, submission=submission)
                unlock_puzzles(submission.team)
        logger.info("Team %s correctly solved puzzle %s" %
                    (str(submission.team.team_name), str(submission.puzzle.puzzle_id)))
        if(regex_response != ""):
            response = regex_response
        else:
            response = "Correct!"

    else:
        if(regex_response != ""):
            response = regex_response
        else:
            response = ""
        logger.info("Team %s incorrectly guessed %s for puzzle %s" %
                    (str(submission.team.team_name), str(submission.submission_text),
                     str(submission.puzzle.puzzle_id)))

    # After the hunt is over, if it's not right it's wrong.
    if(submission.puzzle.hunt.is_public):
        if(response == ""):
            response = "Wrong Answer."

    # This turns on "auto-canned-response"
    if(response == ""):
        response = "Wrong Answer."

    submission.response_text = response
    submission.save()
    return response


# Looks through each puzzle and sees if a team has enough solves to unlock it
# Should be called after anything could add a solve object to a team
# Is also called at the start to release initial puzzles (puzzles with 0 reqs)
# It is implemented using this weird list method to allow for gaps in numbering
def unlock_puzzles(team):
    puzzles = team.hunt.puzzle_set.all().order_by('puzzle_number')
    numbers = []
    # replace with a map?
    for puzzle in puzzles:
        numbers.append(puzzle.puzzle_number)
    # make an array for how many points a team has towards unlocking each puzzle
    mapping = [0 for i in range(max(numbers)+1)]
    # go through each solved puzzle and add to the list for each puzzle it unlocks
    for puzzle in team.solved.all():
        for other in puzzle.unlocks.all():
            mapping[other.puzzle_number] = mapping[other.puzzle_number]+1
    # See if the number of points is enough to unlock any given puzzle
    for puzzle in puzzles:
        if(puzzle.num_required_to_unlock <= mapping[puzzle.puzzle_number]):
            if(puzzle not in team.unlocked.all()):
                logger.info("Team %s unlocked puzzle %s" % (str(team.team_name), str(puzzle.puzzle_id)))
                Unlock.objects.create(team=team, puzzle=puzzle, time=timezone.now())


def download_zip(directory, filename, url):
    if(url == ""):
        return

    logger.info("Attempting to download zip %s to %s/%s" % (url, directory, filename))

    if(not os.path.isdir(directory)):
        call(["mkdir", directory])

    file_str = directory + "/" + filename + ".zip"
    call(["wget", "--max-redirect=20", url, "-O", file_str])
    call(["unzip", "-o", "-d", directory + "/" + filename, file_str])


def download_pdf(directory, filename, url):
    if(url == ""):
        return

    logger.info("Attempting to download pdf %s to %s/%s" % (url, directory, filename))

    if(not os.path.isdir(directory)):
        call(["mkdir", directory])

    file_str = directory + "/" + filename + ".pdf"
    call(["wget", url, "-O", file_str])
    with open(file_str, "rb") as f:
        num_pages = PdfFileReader(f).getNumPages()
    call(["convert", "-density", "200", file_str, directory + "/" + filename + ".png"])
    return num_pages


def download_puzzle(puzzle):
    directory = settings.MEDIA_ROOT + "puzzles"

    puzzle.num_pages = download_pdf(directory, str(puzzle.puzzle_id), puzzle.link)
    puzzle.save()

    download_zip(directory, str(puzzle.puzzle_id), puzzle.resource_link)
    download_pdf(settings.MEDIA_ROOT + "solutions", str(puzzle.puzzle_id), puzzle.solution_link)


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
