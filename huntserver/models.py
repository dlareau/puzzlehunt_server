from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Hunt(models.Model):
    hunt_name = models.CharField(max_length=200)
    hunt_number = models.IntegerField(unique=True)
    start_date = models.DateTimeField()
    
    def __unicode__(self):
        return self.hunt_name

class Puzzle(models.Model):
    puzzle_number = models.IntegerField()
    puzzle_name = models.CharField(max_length=200)
    puzzle_id = models.CharField(max_length=8, unique=True) #hex only please
    answer = models.CharField(max_length=100)
    link = models.URLField(max_length=200)
    num_required_to_unlock = models.IntegerField(default=1)
    unlocks = models.ManyToManyField("self", blank=True, symmetrical=False)
    hunt = models.ForeignKey(Hunt)
    #Reward upon completion? 
    
    def __unicode__(self):
        return self.puzzle_name
    
class Team(models.Model):
    team_name = models.CharField(max_length=200)
    solved = models.ManyToManyField(Puzzle, blank=True, related_name='solved_for', through="Solve")
    unlocked = models.ManyToManyField(Puzzle, blank=True, related_name='unlocked_for', through="Unlock")
    login_info = models.ForeignKey(User)
    hunt = models.ForeignKey(Hunt)

    def __unicode__(self):
        return self.team_name

class Person(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    comments = models.CharField(max_length=400)
    team = models.ForeignKey(Team)
    
    def __unicode__(self):
        return self.first_name + self.last_name
    
class Submission(models.Model):
    team = models.ForeignKey(Team)
    submission_time = models.DateTimeField()
    submission_text = models.CharField(max_length=100)
    response_text = models.CharField(blank=True, max_length=400)
    puzzle = models.ForeignKey(Puzzle)
    
    def __unicode__(self):
        return self.submission_text

class Solve(models.Model):
    puzzle = models.ForeignKey(Puzzle)
    team = models.ForeignKey(Team)
    submission = models.ForeignKey(Submission, blank=True)
    
class Unlock(models.Model):
    puzzle = models.ForeignKey(Puzzle)
    team = models.ForeignKey(Team)
    time = models.DateTimeField()

    def __unicode__(self):
        return self.team.team_name + ": " + self.puzzle.puzzle_name
