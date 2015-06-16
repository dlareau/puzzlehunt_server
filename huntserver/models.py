from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Hunt(models.Model):
    hunt_name = models.CharField(max_length=200)
    start_date = models.DateTimeField()

class Puzzle(models.Model):
    puzzle_number = models.IntegerField(unique=True)
    answer = models.CharField(max_length=100)
    link = models.URLField(max_length=200)
    num_required_to_unlock = models.IntegerField(default=1)
    unlocks = models.ManyToManyField("self")
    hunt = models.ForeignKey(Hunt)
    #Reward upon completion? 
    
class Team(models.Model):
    team_name = models.CharField(max_length=200)
    solved = models.ManyToManyField(Puzzle)
    login_info = models.ForeignKey(User)
    hunt = models.ForeignKey(Hunt)

class Person(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    comments = models.CharField(max_length=400)
    team = models.ForeignKey(Team)
    
class Submission(models.Model):
    team = models.ForeignKey(Team)
    submission_time = models.DateTimeField()
    submission_text = models.CharField(max_length=100)
    response_text = models.CharField(max_length=400)