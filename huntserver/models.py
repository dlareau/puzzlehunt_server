from django.db import models, transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.dateformat import DateFormat
from django.utils.encoding import python_2_unicode_compatible
from dateutil import tz
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import re
import zipfile
import shutil

import logging
logger = logging.getLogger(__name__)

time_zone = tz.gettz(settings.TIME_ZONE)


# TODO: cleanup duplicate functions
def get_puzzle_file_path(puzzle, filename):
    return "puzzles/" + puzzle.puzzle_id + "." + filename.split('.')[-1]


def get_solution_file_path(puzzle, filename):
    return "solutions/" + puzzle.puzzle_id + "_sol." + filename.split('.')[-1]


def get_prepuzzle_file_path(prepuzzle, filename):
    return "prepuzzles/" + str(prepuzzle.pk) + "." + filename.split('.')[-1]


def get_hunt_file_path(hunt, filename):
    return "hunt/" + str(hunt.hunt_number) + "." + filename.split('.')[-1]


class PuzzleOverwriteStorage(FileSystemStorage):
    """ A custom storage class that just overwrites existing files rather than erroring """
    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
            extension = name.split('.')[-1]
            folder = "".join(name.split('.')[:-1])
            if(extension == "zip"):
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT, folder), ignore_errors=True)
        return name

    def url(self, name):
        return settings.PROTECTED_URL + name

    def _save(self, name, content):
        rc = super(PuzzleOverwriteStorage, self)._save(name, content)
        extension = name.split('.')[-1]
        folder = "".join(name.split('.')[:-1])
        if(extension == "zip"):
            with zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, name), "r") as zip_ref:
                zip_ref.extractall(path=os.path.join(settings.MEDIA_ROOT, folder))
        return rc


@python_2_unicode_compatible
class Hunt(models.Model):
    """ Base class for a hunt. Contains basic details about a puzzlehunt. """

    class Meta:
        indexes = [
            models.Index(fields=['hunt_number']),
        ]

    hunt_name = models.CharField(
        max_length=200,
        help_text="The name of the hunt as the public will see it")
    hunt_number = models.IntegerField(
        unique=True,
        help_text="A number used internally for hunt sorting, must be unique")
    team_size = models.IntegerField()
    start_date = models.DateTimeField(
        help_text="The date/time at which a hunt will become visible to registered users")
    end_date = models.DateTimeField(
        help_text="The date/time at which a hunt will be archived and available to the public")
    display_start_date = models.DateTimeField(
        help_text="The start date/time displayed to users")
    display_end_date = models.DateTimeField(
        help_text="The end date/time displayed to users")
    location = models.CharField(
        max_length=100,
        help_text="Starting location of the puzzlehunt")
    resource_file = models.FileField(
        upload_to=get_hunt_file_path,
        storage=PuzzleOverwriteStorage(),
        blank=True,
        help_text="Hunt resources, MUST BE A ZIP FILE.")
    is_current_hunt = models.BooleanField(
        default=False)
    extra_data = models.CharField(
        max_length=200,
        blank=True,
        help_text="A misc. field for any extra data to be stored with the hunt.")
    template = models.TextField(
        default="",
        help_text="The template string to be rendered to HTML on the hunt page")
    hint_lockout = models.IntegerField(
        default=settings.DEFAULT_HINT_LOCKOUT,
        help_text="The number of minutes before a hint can be used on a newly unlocked puzzle")
    points_per_minute = models.IntegerField(
        default=0,
        help_text="The number of points granted per minute during the hunt")

    def clean(self, *args, **kwargs):
        """ Overrides the standard clean method to ensure that only one hunt is the current hunt """
        if(not self.is_current_hunt):
            try:
                old_obj = Hunt.objects.get(pk=self.pk)
                if(old_obj.is_current_hunt):
                    raise ValidationError({'is_current_hunt':
                                           ["There must always be one current hunt", ]})
            except ObjectDoesNotExist:
                pass
        super(Hunt, self).clean(*args, **kwargs)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """ Overrides the standard save method to ensure that only one hunt is the current hunt """
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
    def is_day_of_hunt(self):
        """ A boolean indicating whether or not today is the day of the hunt """
        return timezone.now().date() == self.start_date.date()

    @property
    def in_reg_lockdown(self):
        """ A boolean indicating whether or not registration has locked for this hunt """
        return (self.start_date - timezone.now()).days <= settings.HUNT_REGISTRATION_LOCKOUT

    @property
    def season(self):
        """ Gets a season string from the hunt dates """
        if(self.start_date.month >= 1 and self.start_date.month <= 5):
            return "Spring"
        elif(self.start_date.month >= 8 and self.start_date.month <= 12):
            return "Fall"
        else:
            return "Summer"

    @property
    def real_teams(self):
        """ A queryset of all non-dummy teams in the hunt """
        return self.team_set.exclude(location="DUMMY").all()

    @property
    def dummy_team(self):
        """ The dummy team for the hunt """
        try:
            team = self.team_set.get(location="DUMMY")
        except Team.DoesNotExist:
            team = Team.objects.create(team_name=self.hunt_name + "_DUMMY", hunt=self,
                                       location="DUMMY", join_code="WRONG")
        return team

    def __str__(self):
        if(self.is_current_hunt):
            return self.hunt_name + " (c)"
        else:
            return self.hunt_name

    def team_from_user(self, user):
        """ Takes a user and a hunt and returns either the user's team for that hunt or None """
        if(not user.is_authenticated):
            return None
        teams = get_object_or_404(Person, user=user).teams.filter(hunt=self)
        return teams[0] if (len(teams) > 0) else None


@python_2_unicode_compatible
class Puzzle(models.Model):
    """ A class representing a puzzle within a hunt """

    class Meta:
        indexes = [
            models.Index(fields=['puzzle_id']),
        ]
        ordering = ['-hunt', 'puzzle_number']

    SOLVES_UNLOCK = 'SOL'
    POINTS_UNLOCK = 'POT'
    EITHER_UNLOCK = 'ETH'
    BOTH_UNLOCK = 'BTH'

    puzzle_unlock_type_choices = [
        (SOLVES_UNLOCK, 'Solves Based Unlock'),
        (POINTS_UNLOCK, 'Points Based Unlock'),
        (EITHER_UNLOCK, 'Either (OR) Unlocking Method'),
        (BOTH_UNLOCK, 'Both (AND) Unlocking Methods'),
    ]

    PDF_PUZZLE = 'PDF'
    LINK_PUZZLE = 'LNK'
    WEB_PUZZLE = 'WEB'

    puzzle_page_type_choices = [
        (PDF_PUZZLE, 'Puzzle page displays a PDF'),
        (LINK_PUZZLE, 'Puzzle page links a webpage'),
        (WEB_PUZZLE, 'Puzzle page displays a webpage'),
    ]

    hunt = models.ForeignKey(
        Hunt,
        on_delete=models.CASCADE,
        help_text="The hunt that this puzzle is a part of")
    puzzle_name = models.CharField(
        max_length=200,
        help_text="The name of the puzzle as it will be seen by hunt participants")
    puzzle_number = models.IntegerField(
        help_text="The number of the puzzle within the hunt, for sorting purposes")
    puzzle_id = models.CharField(
        max_length=8,
        unique=True,  # hex only please
        help_text="A 3-5 character hex string that uniquely identifies the puzzle")
    answer = models.CharField(
        max_length=100,
        help_text="The answer to the puzzle, not case sensitive")
    is_meta = models.BooleanField(
        default=False,
        verbose_name="Is a metapuzzle",
        help_text="Is this puzzle a meta-puzzle?")
    puzzle_page_type = models.CharField(
        max_length=3,
        choices=puzzle_page_type_choices,
        default=WEB_PUZZLE,
        blank=False,
        help_text="The type of webpage for this puzzle."
    )
    doesnt_count = models.BooleanField(
        default=False,
        help_text="Should this puzzle not count towards scoring?")
    puzzle_file = models.FileField(
        upload_to=get_puzzle_file_path,
        storage=PuzzleOverwriteStorage(),
        blank=True,
        help_text="Puzzle file. MUST BE A PDF")
    resource_file = models.FileField(
        upload_to=get_puzzle_file_path,
        storage=PuzzleOverwriteStorage(),
        blank=True,
        help_text="Puzzle resources, MUST BE A ZIP FILE.")
    solution_is_webpage = models.BooleanField(
        default=False,
        help_text="Is this solution an html webpage?")
    solution_file = models.FileField(
        upload_to=get_solution_file_path,
        storage=PuzzleOverwriteStorage(),
        blank=True,
        help_text="Puzzle solution. MUST BE A PDF.")
    solution_resource_file = models.FileField(
        upload_to=get_solution_file_path,
        storage=PuzzleOverwriteStorage(),
        blank=True,
        help_text="Puzzle solution resources, MUST BE A ZIP FILE.")
    extra_data = models.CharField(
        max_length=200,
        blank=True,
        help_text="A misc. field for any extra data to be stored with the puzzle.")

    # Unlocking:
    unlock_type = models.CharField(
        max_length=3,
        choices=puzzle_unlock_type_choices,
        default=SOLVES_UNLOCK,
        blank=False,
        help_text="The type of puzzle unlocking scheme"
    )
    num_required_to_unlock = models.IntegerField(
        default=1,
        help_text="Number of prerequisite puzzles that need to be solved to unlock this puzzle")
    unlocks = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        help_text="Puzzles that this puzzle is a possible prerequisite for")
    points_cost = models.IntegerField(
        default=0,
        help_text="The number of points needed to unlock this puzzle.")
    points_value = models.IntegerField(
        default=0,
        help_text="The number of points this puzzle grants upon solving.")

    # Overridden to delete old files on clear
    def save(self, *args, **kwargs):
        if(self.pk):
            # TODO: Clean up this repetitive code
            old_obj = Puzzle.objects.get(pk=self.pk)
            if(self.puzzle_file.name == "" and old_obj.puzzle_file.name != ""):
                full_name = os.path.join(settings.MEDIA_ROOT, old_obj.puzzle_file.name)
                extension = old_obj.puzzle_file.name.split('.')[-1]
                folder = "".join(old_obj.puzzle_file.name.split('.')[:-1])
                if(extension == "zip"):
                    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, folder), ignore_errors=True)
                if os.path.exists(full_name):
                    os.remove(full_name)
            if(self.resource_file.name == "" and old_obj.resource_file.name != ""):
                full_name = os.path.join(settings.MEDIA_ROOT, old_obj.resource_file.name)
                extension = old_obj.resource_file.name.split('.')[-1]
                folder = "".join(old_obj.resource_file.name.split('.')[:-1])
                if(extension == "zip"):
                    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, folder), ignore_errors=True)
                if os.path.exists(full_name):
                    os.remove(full_name)
            if(self.solution_file.name == "" and old_obj.solution_file.name != ""):
                full_name = os.path.join(settings.MEDIA_ROOT, old_obj.solution_file.name)
                extension = old_obj.solution_file.name.split('.')[-1]
                folder = "".join(old_obj.solution_file.name.split('.')[:-1])
                if(extension == "zip"):
                    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, folder), ignore_errors=True)
                if os.path.exists(full_name):
                    os.remove(full_name)
            old_name = old_obj.solution_resource_file.name
            if(self.solution_resource_file.name == "" and old_name != ""):
                full_name = os.path.join(settings.MEDIA_ROOT, old_obj.solution_resource_file.name)
                extension = old_obj.solution_resource_file.name.split('.')[-1]
                folder = "".join(old_obj.solution_resource_file.name.split('.')[:-1])
                if(extension == "zip"):
                    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, folder), ignore_errors=True)
                if os.path.exists(full_name):
                    os.remove(full_name)

        super(Puzzle, self).save(*args, **kwargs)

    def serialize_for_ajax(self):
        """ Serializes the ID, puzzle_number and puzzle_name fields for ajax transmission """
        message = dict()
        message['id'] = self.puzzle_id
        message['number'] = self.puzzle_number
        message['name'] = self.puzzle_name
        return message

    @property
    def safename(self):
        name = self.puzzle_name.lower().replace(" ", "_")
        return re.sub(r'[^a-z_]', '', name)

    def __str__(self):
        return str(self.puzzle_number) + "-" + str(self.puzzle_id) + " " + self.puzzle_name


@python_2_unicode_compatible
class Prepuzzle(models.Model):
    """ A class representing a pre-puzzle within a hunt """

    puzzle_name = models.CharField(
        max_length=200,
        help_text="The name of the puzzle as it will be seen by hunt participants")
    released = models.BooleanField(
        default=False)
    hunt = models.OneToOneField(
        Hunt,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The hunt that this puzzle is a part of, leave blank for no associated hunt.")
    answer = models.CharField(
        max_length=100,
        help_text="The answer to the puzzle, not case sensitive")
    template = models.TextField(
        default='{% extends "prepuzzle.html" %}\r\n{% load prepuzzle_tags %}\r\n' +
                '\r\n{% block content %}\r\n{% endblock content %}',
        help_text="The template string to be rendered to HTML on the hunt page")
    resource_file = models.FileField(
        upload_to=get_prepuzzle_file_path,
        storage=PuzzleOverwriteStorage(),
        blank=True,
        help_text="Prepuzzle resources, MUST BE A ZIP FILE.")
    response_string = models.TextField(
        default="",
        help_text="Data returned to the webpage for use upon solving.")

    def __str__(self):
        if(self.hunt):
            return "prepuzzle " + str(self.pk) + " (" + str(self.hunt.hunt_name) + ")"
        else:
            return "prepuzzle " + str(self.pk)

    # Overridden to delete old files on clear
    def save(self, *args, **kwargs):
        if(self.resource_file.name == ""):
            old_obj = Prepuzzle.objects.get(pk=self.pk)
            if(old_obj.resource_file.name != ""):
                extension = old_obj.resource_file.name.split('.')[-1]
                folder = "".join(old_obj.resource_file.name.split('.')[:-1])
                if(extension == "zip"):
                    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, folder), ignore_errors=True)
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, old_obj.resource_file.name)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, old_obj.resource_file.name))
        super(Prepuzzle, self).save(*args, **kwargs)


class TeamManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (models.Q(team_name__icontains=query) |
                         models.Q(location__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs


@python_2_unicode_compatible
class Team(models.Model):
    """ A class representing a team within a hunt """

    team_name = models.CharField(
        max_length=200,
        help_text="The team name as it will be shown to hunt participants")
    solved = models.ManyToManyField(
        Puzzle,
        blank=True,
        related_name='solved_for',
        through="Solve",
        help_text="The puzzles the team has solved")
    unlocked = models.ManyToManyField(
        Puzzle,
        blank=True,
        related_name='unlocked_for',
        through="Unlock",
        help_text="The puzzles the team has unlocked")
    unlockables = models.ManyToManyField(
        "Unlockable",
        blank=True,
        help_text="The unlockables the team has earned")
    hunt = models.ForeignKey(
        Hunt,
        on_delete=models.CASCADE,
        help_text="The hunt that the team is a part of")
    location = models.CharField(
        max_length=80,
        blank=True,
        help_text="The physical location that the team is solving at")
    join_code = models.CharField(
        max_length=5,
        help_text="The 5 character random alphanumeric password needed for a user to join a team")
    playtester = models.BooleanField(
        default=False,
        help_text="A boolean to indicate if the team is a playtest team and will get early access")
    playtest_start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date/time at which a hunt will become to the playtesters")
    playtest_end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date/time at which a hunt will no longer be available to playtesters")
    num_waiting_messages = models.IntegerField(
        default=0,
        help_text="The number of unseen messages a team has waiting")
    num_available_hints = models.IntegerField(
        default=0,
        help_text="The number of hints the team has available to use")
    num_unlock_points = models.IntegerField(
        default=0,
        help_text="The number of points the team has earned")

    objects = TeamManager()

    @property
    def is_playtester_team(self):
        """ A boolean indicating whether or not the team is a playtesting team """
        return self.playtester

    @property
    def playtest_started(self):
        """ A boolean indicating whether or not the team is currently allowed to be playtesting """
        if(self.playtest_start_date is None or self.playtest_end_date is None):
            return False
        return (timezone.now() >= self.playtest_start_date)

    @property
    def playtest_over(self):
        """ A boolean indicating whether or not the team's playtest slot has passed """
        if(self.playtest_start_date is None or self.playtest_end_date is None):
            return False
        return timezone.now() >= self.playtest_end_date

    @property
    def playtest_happening(self):
        """ A boolean indicating whether or not the team's playtest slot is currently happening """
        return self.playtest_started and not self.playtest_over

    @property
    def is_normal_team(self):
        """ A boolean indicating whether or not the team is a normal (non-playtester) team """
        return (not self.playtester)

    @property
    def short_name(self):
        """ Team name shortened to 30 characters for more consistent display """
        if(len(self.team_name) > 30):
            return self.team_name[:30] + "..."
        else:
            return self.team_name

    @property
    def size(self):
        """ The number of people on the team """
        return self.person_set.count()

    def hints_open_for_puzzle(self, puzzle):
        """ Takes a puzzle and returns whether or not the team may use hints on the puzzle """
        if(self.num_available_hints > 0 or self.hint_set.count() > 0):
            try:
                unlock = Unlock.objects.get(team=self, puzzle=puzzle)
            except Unlock.DoesNotExist:
                return False

            return (timezone.now() - unlock.time).total_seconds() > 60 * self.hunt.hint_lockout
        else:
            return False

    def unlock_puzzles(self):
        """ Unlocks all puzzles a team is currently supposed to have unlocked """
        puzzles = self.hunt.puzzle_set.all().order_by('puzzle_number')
        numbers = []

        numbers = puzzles.values_list('puzzle_number', flat=True)
        # make an array for how many points a team has towards unlocking each puzzle
        mapping = [0 for i in range(max(numbers) + 1)]

        # go through each solved puzzle and add to the list for each puzzle it unlocks
        for puzzle in self.solved.all():
            for num in puzzle.unlocks.values_list('puzzle_number', flat=True):
                mapping[num] += 1

        # See if the number of points is enough to unlock any given puzzle
        puzzles = puzzles.difference(self.unlocked.all())
        for puzzle in puzzles:
            s_unlock = (puzzle.num_required_to_unlock <= mapping[puzzle.puzzle_number])
            p_unlock = (self.num_unlock_points >= puzzle.points_cost)

            if(puzzle.unlock_type == Puzzle.SOLVES_UNLOCK and s_unlock):
                logger.info("Team %s unlocked puzzle %s with solves" % (str(self.team_name),
                            str(puzzle.puzzle_id)))
                Unlock.objects.create(team=self, puzzle=puzzle, time=timezone.now())
            elif(puzzle.unlock_type == Puzzle.POINTS_UNLOCK and p_unlock):
                logger.info("Team %s unlocked puzzle %s with points" % (str(self.team_name),
                            str(puzzle.puzzle_id)))
                Unlock.objects.create(team=self, puzzle=puzzle, time=timezone.now())
            elif(puzzle.unlock_type == Puzzle.EITHER_UNLOCK and (s_unlock or p_unlock)):
                logger.info("Team %s unlocked puzzle %s with either" % (str(self.team_name),
                            str(puzzle.puzzle_id)))
                Unlock.objects.create(team=self, puzzle=puzzle, time=timezone.now())
            elif(puzzle.unlock_type == Puzzle.BOTH_UNLOCK and (s_unlock and p_unlock)):
                logger.info("Team %s unlocked puzzle %s with both" % (str(self.team_name),
                            str(puzzle.puzzle_id)))
                Unlock.objects.create(team=self, puzzle=puzzle, time=timezone.now())

    def unlock_hints(self):
        """ Gives teams the appropriate number of hints based on "Solves" HintUnlockPlans """
        # The way this works currently sucks, it should only be called once per solve
        # Right now that one place is Submission.respond()
        # It also only does # of solves based unlocks. Time based unlocks are done in run_updates
        num_solved = self.solved.count()
        plans = self.hunt.hintunlockplan_set
        num_hints = plans.filter(unlock_type=HintUnlockPlan.SOLVES_UNLOCK,
                                 unlock_parameter=num_solved).count()
        self.num_available_hints = models.F('num_available_hints') + num_hints
        self.save()

    def reset(self):
        """ Resets/deletes all of the team's progress """
        self.unlock_set.all().delete()
        self.unlocked.clear()
        self.solve_set.all().delete()
        self.solved.clear()
        self.submission_set.all().delete()
        self.num_available_hints = 0
        self.num_unlock_points = 0
        self.save()

    def __str__(self):
        return str(self.size) + " (" + self.location + ") " + self.short_name


class PersonManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (models.Q(user__username__icontains=query) |
                         models.Q(user__first_name__icontains=query) |
                         models.Q(user__last_name__icontains=query) |
                         models.Q(user__email__icontains=query))
            qs = qs.filter(or_lookup).distinct()
        return qs


@python_2_unicode_compatible
class Person(models.Model):
    """ A class to associate more personal information with the default django auth user class """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text="The corresponding user to this person")
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Person's phone number, no particular formatting")
    allergies = models.CharField(
        max_length=400,
        blank=True,
        help_text="Allergy information for the person")
    comments = models.CharField(
        max_length=400,
        blank=True,
        help_text="Comments or other notes about the person")
    teams = models.ManyToManyField(
        Team,
        blank=True,
        help_text="Teams that the person is on")
    is_shib_acct = models.BooleanField(
        help_text="A boolean to indicate if the person uses shibboleth authentication for login")

    objects = PersonManager()

    def __str__(self):
        name = self.user.first_name + " " + self.user.last_name + " (" + self.user.username + ")"
        if(name == "  ()"):
            return "Anonymous User"
        else:
            return name

    @property
    def formatted_phone_number(self):
        match = re.match("(?:\\+?1 ?-?)?\\(?([0-9]{3})\\)?-? ?([0-9]{3})-? ?([0-9]{4})", self.phone)
        if(match):
            return match.expand("(\\1)-\\2-\\3")
        return self.phone


@python_2_unicode_compatible
class Submission(models.Model):
    """ A class representing a submission to a given puzzle from a given team """

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text="The team that made the submission")
    submission_time = models.DateTimeField()
    submission_text = models.CharField(
        max_length=100)
    response_text = models.CharField(
        blank=True,
        max_length=400,
        help_text="Response to the given answer. Empty string indicates human response needed")
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
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
        return self.submission_text.upper() == self.puzzle.answer.upper()

    @property
    def convert_markdown_response(self):
        """ The response with all markdown links converted to HTML links """
        return re.sub(r'\[(.*?)\]\((.*?)\)', '<a href="\\2">\\1</a>', self.response_text)

    def save(self, *args, **kwargs):
        """ Overrides the default save function to update the modified date on save """
        self.modified_date = timezone.now()
        super(Submission, self).save(*args, **kwargs)

    def create_solve(self):
        """ Creates a solve based on this submission """
        Solve.objects.create(puzzle=self.puzzle, team=self.team, submission=self)
        logger.info("Team %s correctly solved puzzle %s" % (str(self.team.team_name),
                                                            str(self.puzzle.puzzle_id)))

    # Automatic submission response system
    # Returning an empty string means that huntstaff should respond via the queue
    # Order of response importance: Regex, Defaults, Staff response.
    def respond(self):
        """ Takes the submission's text and uses various methods to craft and populate a response.
            If the response is correct a solve is created and the correct puzzles are unlocked """
        # Compare against correct answer
        if(self.is_correct):
            # Make sure we don't have duplicate or after hunt submission objects
            if(not self.puzzle.hunt.is_public):
                if(self.puzzle not in self.team.solved.all()):
                    self.create_solve()
                    t = self.team
                    t.num_unlock_points = models.F('num_unlock_points') + self.puzzle.points_value
                    t.save()
                    t.refresh_from_db()
                    t.unlock_puzzles()
                    t.unlock_hints()  # The one and only place to call unlock hints

        # Check against regexes
        for resp in self.puzzle.response_set.all():
            if(re.match(resp.regex, self.submission_text, re.IGNORECASE)):
                response = resp.text
                break
        else:  # Give a default response if no regex matches
            if(self.is_correct):
                response = "Correct"
            else:
                # Current philosphy is to auto-can wrong answers: If it's not right, it's wrong
                response = "Wrong Answer."
                logger.info("Team %s incorrectly guessed %s for puzzle %s" %
                            (str(self.team.team_name), str(self.submission_text),
                             str(self.puzzle.puzzle_id)))

        self.response_text = response
        self.save()

    def update_response(self, text):
        """ Updates the response with the given text """
        self.response_text = text
        self.modified_date = timezone.now()  # TODO: I think this line is useless because of ^ save
        self.save()

    def __str__(self):
        return self.submission_text


@python_2_unicode_compatible
class Solve(models.Model):
    """ A class that links a team and a puzzle to indicate that the team has solved the puzzle """

    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        help_text="The puzzle that this is a solve for")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text="The team that this solve is from")
    submission = models.ForeignKey(
        Submission,
        blank=True,
        on_delete=models.CASCADE,
        help_text="The submission object that the team submitted to solve the puzzle")

    class Meta:
        unique_together = ('puzzle', 'team',)

    def serialize_for_ajax(self):
        """ Serializes the puzzle, team, time, and status fields for ajax transmission """
        message = dict()
        message['puzzle'] = self.puzzle.serialize_for_ajax()
        message['team_pk'] = self.team.pk
        time = self.submission.submission_time
        df = DateFormat(time.astimezone(time_zone))
        message['time_str'] = df.format("h:i a")
        message['status_type'] = "solve"
        return message

    def __str__(self):
        return self.team.short_name + " => " + self.puzzle.puzzle_name


@python_2_unicode_compatible
class Unlock(models.Model):
    """ A class that links a team and a puzzle to indicate that the team has unlocked the puzzle """

    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        help_text="The puzzle that this is an unlock for")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text="The team that this unlocked puzzle is for")
    time = models.DateTimeField(
        help_text="The time this puzzle was unlocked for this team")

    class Meta:
        unique_together = ('puzzle', 'team',)

    def serialize_for_ajax(self):
        """ Serializes the puzzle, team, and status fields for ajax transmission """
        message = dict()
        message['puzzle'] = self.puzzle.serialize_for_ajax()
        message['team_pk'] = self.team.pk
        message['status_type'] = "unlock"
        return message

    def __str__(self):
        return self.team.short_name + ": " + self.puzzle.puzzle_name


@python_2_unicode_compatible
class Message(models.Model):
    """ A class that represents a message sent using the chat functionality """

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text="The team that this message is being sent to/from")
    is_response = models.BooleanField(
        help_text="A boolean representing whether or not the message is from the staff")
    text = models.CharField(
        max_length=400,
        help_text="Message text")
    time = models.DateTimeField(
        help_text="Message send time")

    def __str__(self):
        return self.team.short_name + ": " + self.text


@python_2_unicode_compatible
class Unlockable(models.Model):
    """ A class that represents an object to be unlocked after solving a puzzle """

    TYPE_CHOICES = (
        ('IMG', 'Image'),
        ('PDF', 'PDF'),
        ('TXT', 'Text'),
        ('WEB', 'Link'),
    )
    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        help_text="The puzzle that needs to be solved to unlock this object")
    content_type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        default='TXT',
        help_text="The type of object that is to be unlocked, can be 'IMG', 'PDF', 'TXT', or 'WEB'")
    content = models.CharField(
        max_length=500,
        help_text="The link to the content, files must be externally hosted.")

    def __str__(self):
        return "%s (%s)" % (self.puzzle.puzzle_name, self.content_type)


@python_2_unicode_compatible
class Response(models.Model):
    """ A class to represent an automated response regex """

    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        help_text="The puzzle that this automated response is related to")
    regex = models.CharField(
        max_length=400,
        help_text="The python-style regex that will be checked against the user's response")
    text = models.CharField(
        max_length=400,
        help_text="The text to use in the submission response if the regex matched")

    def __str__(self):
        return self.regex + " => " + self.text


@python_2_unicode_compatible
class Hint(models.Model):
    """ A class to represent a hint to a puzzle """

    puzzle = models.ForeignKey(
        Puzzle,
        on_delete=models.CASCADE,
        help_text="The puzzle that this hint is related to")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text="The team that requested the hint")
    request = models.TextField(
        max_length=1000,
        help_text="The text of the request for the hint")
    request_time = models.DateTimeField(
        help_text="Hint request time")
    response = models.TextField(
        max_length=1000,
        blank=True,
        help_text="The text of the response to the hint request")
    response_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Hint response time")
    last_modified_time = models.DateTimeField(
        help_text="Last time of modification")

    def __str__(self):
        return (self.team.short_name + ": " + self.puzzle.puzzle_name +
                " (" + str(self.request_time) + ")")


@python_2_unicode_compatible
class HintUnlockPlan(models.Model):
    """ A class to represent when Teams are given hints """
    hunt = models.ForeignKey(
        Hunt,
        on_delete=models.CASCADE,
        help_text="The hunt that this hint unlock plan refers to")

    TIMED_UNLOCK = 'TIM'
    INTERVAL_UNLOCK = 'INT'
    SOLVES_UNLOCK = 'SOL'

    hint_unlock_type_choices = [
        (TIMED_UNLOCK, 'Exact Time Unlock'),
        (INTERVAL_UNLOCK, 'Interval Based Unlock'),
        (SOLVES_UNLOCK, 'Solves Based Unlock'),
    ]

    unlock_type = models.CharField(
        max_length=3,
        choices=hint_unlock_type_choices,
        default=TIMED_UNLOCK,
        blank=False,
        help_text="The type of hint unlock plan"
    )

    unlock_parameter = models.IntegerField(
        help_text="Parameter (Time / Interval / Solves)")

    num_triggered = models.IntegerField(
        default=0,
        help_text="Number of times this Unlock Plan has given a hint")

    def reset_plan(self):
        """ Resets the HintUnlockPlan """
        self.num_triggered = 0

    def __str__(self):
        return "Nope"


class OverwriteStorage(FileSystemStorage):
    """ A custom storage class that just overwrites existing files rather than erroring """
    def get_available_name(self, name, max_length=None):
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


@python_2_unicode_compatible
class HuntAssetFile(models.Model):
    """ A class to represent an asset file for a puzzlehunt """
    file = models.FileField(upload_to='hunt/assets/', storage=OverwriteStorage())

    def __str__(self):
        return os.path.basename(self.file.name)
