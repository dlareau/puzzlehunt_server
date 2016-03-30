from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Hunt(models.Model):
    hunt_name = models.CharField(max_length=200)
    hunt_number = models.IntegerField(unique=True)
    team_size = models.IntegerField()
    #Very bad things could happen if end date is before start date
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=100)
    
    @property
    def is_locked(self):
        return timezone.now() < self.start_date

    @property
    def is_open(self):
        return timezone.now() > self.start_date and timezone.now() < self.end_date

    @property
    def is_public(self):
        return timezone.now() > self.end_date

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
    num_pages = models.IntegerField()
    #Reward upon completion? 
    
    def __unicode__(self):
        return str(self.puzzle_number) + "-" + str(self.puzzle_id) + " " + self.puzzle_name
    
class Team(models.Model):
    team_name = models.CharField(max_length=200)
    solved = models.ManyToManyField(Puzzle, blank=True, related_name='solved_for', through="Solve")
    unlocked = models.ManyToManyField(Puzzle, blank=True, related_name='unlocked_for', through="Unlock")
    unlockables = models.ManyToManyField("Unlockable", blank=True)
    hunt = models.ForeignKey(Hunt)
    location = models.CharField(max_length=80, blank=True)
    join_code = models.CharField(max_length=5)

    def __unicode__(self):
        return str(len(self.person_set.all())) + " (" + self.location + ") " + self.team_name

class Person(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=20, blank=True)
    allergies = models.CharField(max_length=400, blank=True)
    comments = models.CharField(max_length=400, blank=True)
    teams = models.ManyToManyField(Team, blank=True)
    is_shib_acct = models.BooleanField()
    
    def __unicode__(self):
        name = self.user.first_name + " " + self.user.last_name + " (" + self.user.email + ")"
        if(name == " "):
            return "Anonymous User"
        else:
            return self.user.first_name + " " + self.user.last_name + " (" + self.user.email + ")"
    
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

    class Meta:
        unique_together = ('puzzle', 'team',)
    
    def __unicode__(self):
        return self.team.team_name + " => " + self.puzzle.puzzle_name
    
class Unlock(models.Model):
    puzzle = models.ForeignKey(Puzzle)
    team = models.ForeignKey(Team)
    time = models.DateTimeField()

    class Meta:
        unique_together = ('puzzle', 'team',)
    
    def __unicode__(self):
        return self.team.team_name + ": " + self.puzzle.puzzle_name

class Message(models.Model):
    team = models.ForeignKey(Team)
    is_response = models.BooleanField()
    text = models.CharField(max_length=400)
    time = models.DateTimeField()

    def __unicode__(self):
        return self.team.team_name + ": " + self.text

class Unlockable(models.Model):
    TYPE_CHOICES = (
        ('IMG', 'Image'),
        ('PDF', 'PDF'),
        ('TXT', 'Text'),
        ('WEB', 'Link'),
    )
    puzzle = models.ForeignKey(Puzzle)
    content_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='TXT')
    content = models.CharField(max_length=500)
    
