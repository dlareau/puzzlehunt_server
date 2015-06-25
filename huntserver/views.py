# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required

from .models import Hunt, Puzzle, Submission, Team, Person

#models needed: puzzle, hunt, index, stats
#for now, index should really just call hunt(highest #)

#code below is from tutorial and will not run properly
@login_required
def hunt(request, hunt_num):
    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    puzzles = sorted(hunt.puzzle_set.all(), key=lambda p: p.puzzle_number)
    return render(request, 'hunt' + str(hunt_num) + '.html', {'puzzles': puzzles})

def index(request):
    newest_hunt = 1 #TODO: fix
    return hunt(request, newest_hunt)

def puzzle(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
    submissions = puzzle.submission_set.all()
    context = {'puzzle': puzzle, 'submission_list': submissions}
    return render(request, 'puzzle.html', context)

#TODO: fix
def public_stats(request):
    newest_hunt = 1
    return hunt(request, newest_hunt)
