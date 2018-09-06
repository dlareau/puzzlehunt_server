from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.dateformat import DateFormat
from dateutil import tz
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import re

time_zone = tz.gettz(settings.TIME_ZONE)

class Hunt(models.Model):
    """ Base class for a hunt. Contains basic details about a puzzlehunt. """

    hunt_name = models.CharField(max_length=200,
        help_text="The name of the hunt as the public will see it")
    hunt_number = models.IntegerField(unique=True,
        help_text="A number used internally for hunt sorting, must be unique")
    team_size = models.IntegerField()
    start_date = models.DateTimeField(
        help_text="The date/time at which a hunt will become visible to registered users")
    end_date = models.DateTimeField(
        help_text="The date/time at which a hunt will be archived and available to the public")
    location = models.CharField(max_length=100,
        help_text="Starting location of the puzzlehunt")
    is_current_hunt = models.BooleanField(default=False)
    template = models.TextField(default="",
        help_text="The template string to be rendered to HTML on the hunt page")

    # A bit of custom logic in clean and save to ensure exactly one hunt's
    # is_current_hunt is true at any time. It makes sure you can never un-set the
    # value, and setting it anywhere else unsets all others.
    def clean(self, *args, **kwargs):
        if(not self.is_current_hunt):
            try:
                old_instance = Hunt.objects.get(pk=self.pk)
                if(old_instance.is_current_hunt):
                    raise ValidationError({'is_current_hunt':
                                           ["There must always be one current hunt", ]})
            except ObjectDoesNotExist:
                pass
        super(Hunt, self).clean(*args, **kwargs)

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        if self.is_current_hunt:
            Hunt.objects.filter(is_current_hunt=True).update(is_current_hunt=False)
        super(Hunt, self).save(*args, **kwargs)

    @property
    def is_locked(self):
        """ A boolean indicating whether or not the hunt is locked """
        return timezone.now() < self.start_date

    @property
    def is_open(self):
        """ A boolean indicating whether or not the hunt is open to registered participants """
        return timezone.now() >= self.start_date and timezone.now() < self.end_date

    @property
    def is_public(self):
        """ A boolean indicating whether or not the hunt is open to the public """
        return timezone.now() > self.end_date

    @property
    def real_teams(self):
        return self.team_set.exclude(location="DUMMY").all()

    def __unicode__(self):
        if(self.is_current_hunt):
            return self.hunt_name + " (c)"
        else:
            return self.hunt_name


class Puzzle(models.Model):
    """ A class representing a puzzle within a hunt """

    puzzle_number = models.IntegerField(
        help_text="The number of the puzzle within the hunt, for sorting purposes")
    puzzle_name = models.CharField(max_length=200,
        help_text="The name of the puzzle as it will be seen by hunt participants")
    puzzle_id = models.CharField(max_length=8, unique=True,  # hex only please
        help_text="A 3 character hex string that uniquely identifies the puzzle")
    answer = models.CharField(max_length=100,
        help_text="The answer to the puzzle, not case sensitive")
    link = models.URLField(max_length=200,
        help_text="The full link (needs http://) to a publicly accessible PDF of the puzzle")
    num_required_to_unlock = models.IntegerField(default=1,
        help_text="Number of prerequisite puzzles that need to be solved to unlock this puzzle")
    unlocks = models.ManyToManyField("self", blank=True, symmetrical=False,
        help_text="Puzzles that this puzzle is a possible prerequisite for")
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE,
        help_text="The hunt that this puzzle is a part of")
    num_pages = models.IntegerField(
        help_text="Number of pages in the PDF for this puzzle. Set automatically upon download")

    def serialize_for_ajax(self):
        """ Serializes the ID, puzzle_number and puzzle_name fields for ajax transmission """
        message = dict()
        message['id'] = self.puzzle_id
        message['number'] = self.puzzle_number
        message['name'] = self.puzzle_name
        return message

    def __unicode__(self):
        return str(self.puzzle_number) + "-" + str(self.puzzle_id) + " " + self.puzzle_name


class Team(models.Model):
    """ A class representing a team within a hunt """

    team_name = models.CharField(max_length=200,
        help_text="The team name as it will be shown to hunt participants")
    solved = models.ManyToManyField(Puzzle, blank=True, related_name='solved_for', through="Solve",
        help_text="The puzzles the team has solved")
    unlocked = models.ManyToManyField(Puzzle, blank=True, related_name='unlocked_for',
        through="Unlock", help_text="The puzzles the team has unlocked")
    unlockables = models.ManyToManyField("Unlockable", blank=True,
        help_text="The unlockables the team has earned")
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE,
        help_text="The hunt that the team is a part of")
    location = models.CharField(max_length=80, blank=True,
        help_text="The physical location that the team is solving at")
    join_code = models.CharField(max_length=5,
        help_text="The 5 character random alphanumeric password needed for a user to join a team")
    playtester = models.BooleanField(default=False,
        help_text="A boolean to indicate if the team is a playtest team and will get early access")

    @property
    def is_playtester_team(self):
        """ A boolean indicating whether or not the team is a playtesting team """
        return self.playtester

    @property
    def is_normal_team(self):
        """ A boolean indicating whether or not the team is a normal (non-playtester) team """
        return (not self.playtester)

    def __unicode__(self):
        return str(self.person_set.count()) + " (" + self.location + ") " + self.team_name


class Person(models.Model):
    """ A class to associate more personal information with the default django auth user class """

    user = models.OneToOneField(User, on_delete=models.CASCADE,
        help_text="The corresponding user to this person")
    phone = models.CharField(max_length=20, blank=True,
        help_text="Person's phone number, no particular formatting")
    allergies = models.CharField(max_length=400, blank=True,
        help_text="Allergy information for the person")
    comments = models.CharField(max_length=400, blank=True,
        help_text="Comments or other notes about the person")
    teams = models.ManyToManyField(Team, blank=True,
        help_text="Teams that the person is on")
    is_shib_acct = models.BooleanField(
        help_text="A boolean to indicate if the person uses shibboleth authentication for login")

    def __unicode__(self):
        name = self.user.first_name + " " + self.user.last_name + " (" + self.user.username + ")"
        if(name == "  ()"):
            return "Anonymous User"
        else:
            return name


class Submission(models.Model):
    """ A class representing a submission to a given puzzle from a given team """

    team = models.ForeignKey(Team, on_delete=models.CASCADE,
        help_text="The team that made the submission")
    submission_time = models.DateTimeField()
    submission_text = models.CharField(max_length=100)
    response_text = models.CharField(blank=True, max_length=400,
        help_text="Response to the given answer. Empty string indicates human response needed")
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE,
        help_text="The puzzle that this submission is in response to")
    modified_date = models.DateTimeField(
        help_text="Last date/time of response modification")

    def serialize_for_ajax(self):
        """ Serializes the time, puzzle, team, and status fields for ajax transmission """
        message = dict()
        df = DateFormat(self.submission_time.astimezone(time_zone))
        message['time_str'] = df.format("h:i a")
        message['puzzle'] = self.puzzle.serialize_for_ajax()
        message['team_pk'] = self.team.pk
        message['status_type'] = "submission"
        return message

    @property
    def is_correct(self):
        """ A boolean indicating if the submission given is exactly correct """
        return self.submission_text.lower() == self.puzzle.answer.lower()

    @property
    def convert_markdown_response(self):
        return re.sub(r'\[(.*?)\]\((.*?)\)', '<a href="\\2">\\1</a>', self.response_text)

    def save(self, *args, **kwargs):
        self.modified_date = timezone.now()
        super(Submission, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.submission_text


class Solve(models.Model):
    """ A class that links a team and a puzzle to indicate that the team has solved the puzzle """

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE,
        help_text="The puzzle that this is a solve for")
    team = models.ForeignKey(Team, on_delete=models.CASCADE,
        help_text="The team that this solve is from")
    submission = models.ForeignKey(Submission, blank=True, on_delete=models.CASCADE,
        help_text="The submission object that the team submitted to solve the puzzle")

    class Meta:
        unique_together = ('puzzle', 'team',)

    def serialize_for_ajax(self):
        """ Serializes the puzzle, team, time, and status fields for ajax transmission """
        message = dict()
        message['puzzle'] = self.puzzle.serialize_for_ajax()
        message['team_pk'] = self.team.pk
        try:
            # Will fail if there is more than one solve per team/puzzle pair
            # That should be impossible, but lets not crash because of it
            time = self.submission.submission_time
            df = DateFormat(time.astimezone(time_zone))
            message['time_str'] = df.format("h:i a")
        except:
            message['time_str'] = "0:00 am"
        message['status_type'] = "solve"
        return message

    def __unicode__(self):
        return self.team.team_name + " => " + self.puzzle.puzzle_name


class Unlock(models.Model):
    """ A class that links a team and a puzzle to indicate that the team has unlocked the puzzle """

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE,
        help_text="The puzzle that this is an unlock for")
    team = models.ForeignKey(Team, on_delete=models.CASCADE,
        help_text="The team that this unlocked puzzle is for")
    time = models.DateTimeField(
        help_text="The time this puzzle was unlocked for this team")

    class Meta:
        unique_together = ('puzzle', 'team',)

    def serialize_for_ajax(self):
        message = dict()
        message['puzzle'] = self.puzzle.serialize_for_ajax()
        message['team_pk'] = self.team.pk
        message['status_type'] = "unlock"
        return message

    def __unicode__(self):
        return self.team.team_name + ": " + self.puzzle.puzzle_name


class Message(models.Model):
    """ A class that represents a message sent using the chat functionality """

    team = models.ForeignKey(Team, on_delete=models.CASCADE,
        help_text="The team that this message is being sent to/from")
    is_response = models.BooleanField(
        help_text="A boolean representing whether or not the message is from the staff")
    text = models.CharField(max_length=400,
        help_text="Message text")
    time = models.DateTimeField(
        help_text="Message send time")

    def __unicode__(self):
        return str(self.team.team_name + ": " + self.text)


class Unlockable(models.Model):
    """ A class that represents an object to be unlocked after solving a puzzle """

    TYPE_CHOICES = (
        ('IMG', 'Image'),
        ('PDF', 'PDF'),
        ('TXT', 'Text'),
        ('WEB', 'Link'),
    )
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE,
        help_text="The puzzle that needs to be solved to unlock this object")
    content_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='TXT',
        help_text="The type of object that is to be unlocked, can be 'IMG', 'PDF', 'TXT', or 'WEB'")
    content = models.CharField(max_length=500,
        help_text="The link to the content, files must be externally hosted.")

    def __unicode__(self):
        return "%s (%s)" % (self.puzzle.puzzle_name, self.content_type)


class Response(models.Model):
    """ A class to represent an automated response regex """

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE,
        help_text="The puzzle that this automated response is related to")
    regex = models.CharField(max_length=400,
        help_text="The python-style regex that will be checked against the user's response")
    text = models.CharField(max_length=400,
        help_text="The text to use in the submission response if the regex matched")

    def __unicode__(self):
        return self.regex + "=>" + self.text


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class HuntAssetFile(models.Model):
    """ A class to represent an asset file for a puzzlehunt """
    file = models.FileField(upload_to='hunt/assets/', storage=OverwriteStorage())

    def __unicode__(self):
        return os.path.basename(self.file.name)
