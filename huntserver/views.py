# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from .models import Hunt, Puzzle

#models needed: puzzle, hunt, index, stats
#for now, index should really just call hunt(highest #)

#code below is from tutorial and will not run properly
def hunt(request, hunt_num):
    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    puzzles = sorted(hunt.puzzle_set.all(), key=lambda p: p.puzzle_number)
    return render(request, 'hunt' + str(hunt_num) + '.html', {'puzzles': puzzles})

def index(request):
    newest_hunt = 1 #TODO: fix
    return hunt(request, newest_hunt)

#TODO: fix
def puzzle(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
    return render(request, 'puzzle.html', {'puzzle': puzzle})

def public_stats(request):
    newest_hunt = 1
    return hunt(request, newest_hunt)