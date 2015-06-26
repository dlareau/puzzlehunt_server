# Create your views here.
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Hunt, Puzzle, Submission, Team, Person
from .forms import AnswerForm

@login_required
def hunt(request, hunt_num):
    hunt = get_object_or_404(Hunt, hunt_number=hunt_num)
    puzzles = sorted(hunt.puzzle_set.all(), key=lambda p: p.puzzle_number)
    return render(request, 'hunt' + str(hunt_num) + '.html', {'puzzles': puzzles})

@login_required
def index(request):
    newest_hunt = 1 #TODO: fix
    return hunt(request, newest_hunt)

@login_required
def puzzle(request, puzzle_id):
    puzzle = get_object_or_404(Puzzle, puzzle_id=puzzle_id)
    team = Team.objects.get(login_info=request.user);
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            user_answer = form.cleaned_data['answer']
            time = timezone.now()
            s = Submission(submission_text=user_answer, submission_time=time,
                           puzzle=puzzle, team=team)
            s.save()
            return HttpResponseRedirect("/puzzle/"+ str(puzzle_id))
            
    submissions = puzzle.submission_set.filter(team=team)
    form = AnswerForm()
    context = {'form': form, 'puzzle': puzzle, 'submission_list': submissions}
    return render(request, 'puzzle.html', context)

#TODO: fix
@login_required
def public_stats(request):
    newest_hunt = 1
    return hunt(request, newest_hunt)
