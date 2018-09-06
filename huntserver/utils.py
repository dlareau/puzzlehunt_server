from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Solve, Unlock, Hunt, Person, Team
from django.utils import timezone
from subprocess import call
import os
from PyPDF2 import PdfFileReader
import re

# Automatic submission response system
# Takes a submission object and should return a string
# Returning an empty string means that huntstaff should respond via the queue
# Currently only invalid characters are spaces and underscores.
# Order of response importance: Correct regex, Correct default,
# Invalid characters, Incorrect regex, Incorrect (archived), Staff response.
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
        if(regex_response != ""):
            response = regex_response
        else:
            response = "Correct!"

    # Currently not used to do punctiation stripping
    # # Answers should not contain spaces
    # elif(" " in submission.submission_text):
    #     response = "Invalid answer (spaces)"
    # # Answers should not contain underscores
    # elif("_" in submission.submission_text):
    #     response = "Invalid answer (underscores)"
    # Check against all expected answers and respond appropriately

    else:
        if(regex_response != ""):
            response = regex_response
        else:
            response = ""

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
                Unlock.objects.create(team=team, puzzle=puzzle, time=timezone.now())

# Runs the commands listed at the bottom for the puzzle to download the pdf
# and convert it to PNGs. Does not provide any roll-back safety if the new PDF
# is bad. Has to also get number of pages for the template rendering
def download_puzzle(puzzle):
    directory = settings.MEDIA_ROOT + "puzzles"

    if(not os.path.isdir(directory)):
        call(["mkdir", directory])

    # Get the file
    file_str = directory + "/" +  puzzle.puzzle_id + ".pdf"
    call(["wget", puzzle.link, "-O", file_str])
    with open(file_str, "rb") as f:
        puzzle.num_pages = PdfFileReader(f).getNumPages()
        puzzle.save()
    call(["convert", "-density", "200", file_str, directory + "/" + puzzle.puzzle_id + ".png"])
    #get document: wget {{URL}} -O {{FILENAME}}
    #convert: convert -density 200 {{FILENAME}} {{OUTFILE}}

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

# This is from an old shibboleth implementation
# Maybe bring this back for login_selection.html
# def build_shib_url(request, target, entityid=None):
#     url_base = 'https://%s' % request.get_host()
#     shib_url = "%s%s" % (url_base, getattr(settings, 'SHIB_HANDLER', '/Shibboleth.sso/DS'))
#     if not target.startswith('http'):
#         target = url_base + target

#     url = '%s?target=%s' % (shib_url, target)
#     if entityid:
#         url += '&entityID=%s' % entityid
#     return url

def dummy_team_from_hunt(hunt):
    try:
        team = Team.objects.get(hunt=hunt, location="DUMMY")
    except:
        team = Team.objects.create(team_name=hunt.hunt_name+"_DUMMY", hunt=hunt,
                    location="DUMMY", join_code="WRONG")
    return team

def team_from_user_hunt(user, hunt):
    if(user.is_anonymous()):
        return None
    teams1 = get_object_or_404(Person, user=user)
    teams = teams1.teams.filter(hunt=hunt)
    if(len(teams) > 0):
        return teams[0]
    else:
        return None
