# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0020_auto_20171008_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hunt',
            name='end_date',
            field=models.DateTimeField(help_text=b'The date/time at which a hunt will be archived and available to the public'),
        ),
        migrations.AlterField(
            model_name='hunt',
            name='hunt_name',
            field=models.CharField(help_text=b'The name of the hunt as the public will see it', max_length=200),
        ),
        migrations.AlterField(
            model_name='hunt',
            name='hunt_number',
            field=models.IntegerField(help_text=b'A number used internally for hunt sorting, must be unique', unique=True),
        ),
        migrations.AlterField(
            model_name='hunt',
            name='location',
            field=models.CharField(help_text=b'Starting location of the puzzlehunt', max_length=100),
        ),
        migrations.AlterField(
            model_name='hunt',
            name='start_date',
            field=models.DateTimeField(help_text=b'The date/time at which a hunt will become visible to registered users'),
        ),
        migrations.AlterField(
            model_name='hunt',
            name='template',
            field=models.TextField(default=b'', help_text=b'The template string to be rendered to HTML on the hunt page'),
        ),
        migrations.AlterField(
            model_name='message',
            name='is_response',
            field=models.BooleanField(help_text=b'A boolean representing whether or not the message is from the staff'),
        ),
        migrations.AlterField(
            model_name='message',
            name='team',
            field=models.ForeignKey(help_text=b'The team that this message is being sent to/from', to='huntserver.Team', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.CharField(help_text=b'Message text', max_length=400),
        ),
        migrations.AlterField(
            model_name='message',
            name='time',
            field=models.DateTimeField(help_text=b'Message send time'),
        ),
        migrations.AlterField(
            model_name='person',
            name='allergies',
            field=models.CharField(help_text=b'Allergy information for the person', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='comments',
            field=models.CharField(help_text=b'Comments or other notes about the person', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='is_shib_acct',
            field=models.BooleanField(help_text=b'A boolean to indicate if the person uses shibboleth authentication for login'),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(help_text=b"Person's phone number, no particular formatting", max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='teams',
            field=models.ManyToManyField(help_text=b'Teams that the person is on', to='huntserver.Team', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, help_text=b'The corresponding user to this person', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='answer',
            field=models.CharField(help_text=b'The answer to the puzzle, not case sensitive', max_length=100),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='hunt',
            field=models.ForeignKey(help_text=b'The hunt that this puzzle is a part of', to='huntserver.Hunt', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='link',
            field=models.URLField(help_text=b'The full link (needs http://) to a publicly accessible PDF of the puzzle'),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='num_pages',
            field=models.IntegerField(help_text=b'Number of pages in the PDF for this puzzle. Set automatically upon download'),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='num_required_to_unlock',
            field=models.IntegerField(default=1, help_text=b'Number of prerequisite puzzles that need to be solved to unlock this puzzle'),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='puzzle_id',
            field=models.CharField(help_text=b'A 3 character hex string that uniquely identifies the puzzle', unique=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='puzzle_name',
            field=models.CharField(help_text=b'The name of the puzzle as it will be seen by hunt participants', max_length=200),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='puzzle_number',
            field=models.IntegerField(help_text=b'The number of the puzzle within the hunt, for sorting purposes'),
        ),
        migrations.AlterField(
            model_name='puzzle',
            name='unlocks',
            field=models.ManyToManyField(help_text=b'Puzzles that this puzzle is a possible prerequisite for', to='huntserver.Puzzle', blank=True),
        ),
        migrations.AlterField(
            model_name='response',
            name='puzzle',
            field=models.ForeignKey(help_text=b'The puzzle that this automated response is related to', to='huntserver.Puzzle', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='response',
            name='regex',
            field=models.CharField(help_text=b"The python-style regex that will be checked against the user's response", max_length=400),
        ),
        migrations.AlterField(
            model_name='response',
            name='text',
            field=models.CharField(help_text=b'The text to use in the submission response if the regex matched', max_length=400),
        ),
        migrations.AlterField(
            model_name='solve',
            name='puzzle',
            field=models.ForeignKey(help_text=b'The puzzle that this is a solve for', to='huntserver.Puzzle', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='solve',
            name='submission',
            field=models.ForeignKey(blank=True, to='huntserver.Submission', help_text=b'The submission object that the team submitted to solve the puzzle', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='solve',
            name='team',
            field=models.ForeignKey(help_text=b'The team that this solve is from', to='huntserver.Team', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='submission',
            name='modified_date',
            field=models.DateTimeField(help_text=b'Last date/time of response modification'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='puzzle',
            field=models.ForeignKey(help_text=b'The puzzle that this submission is in response to', to='huntserver.Puzzle', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='submission',
            name='response_text',
            field=models.CharField(help_text=b'Response to the given answer. Empty string indicates human response needed', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='team',
            field=models.ForeignKey(help_text=b'The team that made the submission', to='huntserver.Team', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='team',
            name='hunt',
            field=models.ForeignKey(help_text=b'The hunt that the team is a part of', to='huntserver.Hunt', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='team',
            name='join_code',
            field=models.CharField(help_text=b'The 5 character random alphanumeric password needed for a user to join a team', max_length=5),
        ),
        migrations.AlterField(
            model_name='team',
            name='location',
            field=models.CharField(help_text=b'The physical location that the team is solving at', max_length=80, blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='playtester',
            field=models.BooleanField(default=False, help_text=b'A boolean to indicate if the team is a playtest team and will get early access'),
        ),
        migrations.AlterField(
            model_name='team',
            name='solved',
            field=models.ManyToManyField(help_text=b'The puzzles the team has solved', related_name='solved_for', through='huntserver.Solve', to='huntserver.Puzzle', blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_name',
            field=models.CharField(help_text=b'The team name as it will be shown to hunt participants', max_length=200),
        ),
        migrations.AlterField(
            model_name='team',
            name='unlockables',
            field=models.ManyToManyField(help_text=b'The unlockables the team has earned', to='huntserver.Unlockable', blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='unlocked',
            field=models.ManyToManyField(help_text=b'The puzzles the team has unlocked', related_name='unlocked_for', through='huntserver.Unlock', to='huntserver.Puzzle', blank=True),
        ),
        migrations.AlterField(
            model_name='unlock',
            name='puzzle',
            field=models.ForeignKey(help_text=b'The puzzle that this is an unlock for', to='huntserver.Puzzle', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='unlock',
            name='team',
            field=models.ForeignKey(help_text=b'The team that this unlocked puzzle is for', to='huntserver.Team', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='unlock',
            name='time',
            field=models.DateTimeField(help_text=b'The time this puzzle was unlocked for this team'),
        ),
        migrations.AlterField(
            model_name='unlockable',
            name='content',
            field=models.CharField(help_text=b'The link to the content, files must be externally hosted.', max_length=500),
        ),
        migrations.AlterField(
            model_name='unlockable',
            name='content_type',
            field=models.CharField(default=b'TXT', help_text=b"The type of object that is to be unlocked, can be 'IMG', 'PDF', 'TXT', or 'WEB'", max_length=3, choices=[(b'IMG', b'Image'), (b'PDF', b'PDF'), (b'TXT', b'Text'), (b'WEB', b'Link')]),
        ),
        migrations.AlterField(
            model_name='unlockable',
            name='puzzle',
            field=models.ForeignKey(help_text=b'The puzzle that needs to be solved to unlock this object', to='huntserver.Puzzle', on_delete=models.CASCADE),
        ),
    ]
