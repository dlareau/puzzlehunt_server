from .models import *
from .redis import *
from django.utils import timezone

def respond_to_submission(submission):
    # Compare against correct answer
    if(submission.puzzle.answer.lower() == submission.submission_text.lower()):
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
    else:
        response = ""

    submission.response_text = response
    submission.save()
    send_submission_update(submission)
    return response

def unlock_puzzles(team):
    puzzles = team.hunt.puzzle_set.all().order_by('puzzle_number')
    numbers = []
    for puzzle in puzzles:
        numbers.append(puzzle.puzzle_number)
    mapping = [0 for i in range(max(numbers)+1)]
    for puzzle in team.solved.all():
        for other in puzzle.unlocks.all():
            mapping[other.puzzle_number] = mapping[other.puzzle_number]+1
    for puzzle in puzzles:
        if(puzzle.num_required_to_unlock <= mapping[puzzle.puzzle_number]):
            if(puzzle not in team.unlocked.all()):
                Unlock.objects.create(team=team, puzzle=puzzle, time=timezone.now())
                send_status_update(puzzle, team, "unlock")
    
def download_puzzles(hunt):
    return
