from .models import *
from .redis import *

def respond_to_submission(s, puzzle):
    # Compare against correct answer
    if(puzzle.answer.lower() == s.submission_text.lower()):
        return "Correct!"
    # Answers should not contain spaces
    elif(" " in s.submission_text):
        return "Invalid answer (spaces)"
    # Answers should not contain underscores
    elif("_" in s.submission_text):
        return "Invalid answer (underscores)"
    else:
        return ""

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
                team.unlocked.add(puzzle)
                send_status_update(puzzle, team, "unlock")
    
        
