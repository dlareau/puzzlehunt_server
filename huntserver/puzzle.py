from .models import *
from .redis import *
from django.conf import settings
from django.utils import timezone
from subprocess import call, check_output
from time import sleep

# Automatic submission response system
# Takes a submission object and should return a string
# Returning an empty string means that huntstaff should respond via the queue
# Currently only stops spaces and underscores.
def respond_to_submission(submission):
    # Compare against correct answer
    if(submission.puzzle.answer.lower() == submission.submission_text.lower()):
        # Make sure we don't have duplicate or after hunt submission objects
        if(submission.puzzle not in submission.team.solved.all()):# and submission.puzzle.hunt.is_open):
            Solve.objects.create(puzzle=submission.puzzle, 
                team=submission.team, submission=submission)
            send_status_update(submission.puzzle, submission.team, "solve")
            unlock_puzzles(submission.team)
        response = "Correct!"
    # Answers should not contain spaces
    elif(" " in submission.submission_text):
        response = "Invalid answer (spaces)"
    # Answers should not contain underscores
    elif("_" in submission.submission_text):
        response = "Invalid answer (underscores)"
    # Let staff respond to everything else
    else:
        response = ""

    # After the hunt is over, if it's not right it's wrong.
    if(submission.puzzle.hunt.is_public):
        if(response == ""):
            response = "wrong answer."
        response = "Hunt is over, but " + response

    submission.response_text = response
    submission.save()
    send_submission_update(submission)
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
                send_status_update(puzzle, team, "unlock")
    
# Runs the commands listed at the bottom for each puzzle to download the pdf 
# and convert it to PNGs. It first clears the old PNGs and PDFs.
# Has to also get number of pages so that the whole pdf doesn't become one image
def download_puzzles(hunt):
    directory = "/home/hunt/puzzlehunt_server/huntserver/static/huntserver/puzzles"
    call(["rm", "-r", directory])
    call(["mkdir", directory])
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    for puzzle in curr_hunt.puzzle_set.all():
        file_str = directory + "/" +  puzzle.puzzle_id + ".pdf"
        call(["wget", puzzle.link, "-O", file_str])
        pages = int(check_output("pdfinfo " + file_str + " | grep Pages | awk '{print $2}'", shell=True))
        for i in range(pages):
            call(["convert", "-density", "200", "-scale", "x1000", file_str + "[" + str(i) + "]", directory + "/" + puzzle.puzzle_id + "-" + str(i) + ".png"])
        
    #get document: wget {{URL}} -O {{FILENAME}}
    #get pages: pdfinfo {{FILENAME}} | grep Pages | awk '{print $2}'
    #convert: convert -density 200 -scale x1000 {{FILENAME}}[i] {{OUTFILE}}

    return
