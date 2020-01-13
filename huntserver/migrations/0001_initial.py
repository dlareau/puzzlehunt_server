# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hunt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hunt_name', models.CharField(max_length=200)),
                ('hunt_number', models.IntegerField(unique=True)),
                ('team_size', models.IntegerField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_response', models.BooleanField()),
                ('text', models.CharField(max_length=400)),
                ('time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('comments', models.CharField(max_length=400, blank=True)),
                ('year', models.IntegerField(null=True, blank=True)),
                ('login_info', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Puzzle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puzzle_number', models.IntegerField()),
                ('puzzle_name', models.CharField(max_length=200)),
                ('puzzle_id', models.CharField(unique=True, max_length=8)),
                ('answer', models.CharField(max_length=100)),
                ('link', models.URLField()),
                ('num_required_to_unlock', models.IntegerField(default=1)),
                ('hunt', models.ForeignKey(to='huntserver.Hunt', on_delete=models.CASCADE)),
                ('unlocks', models.ManyToManyField(to='huntserver.Puzzle', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Solve',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submission_time', models.DateTimeField()),
                ('submission_text', models.CharField(max_length=100)),
                ('response_text', models.CharField(max_length=400, blank=True)),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('team_name', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=80, blank=True)),
                ('hunt', models.ForeignKey(to='huntserver.Hunt', on_delete=models.CASCADE)),
                ('solved', models.ManyToManyField(related_name='solved_for', through='huntserver.Solve', to='huntserver.Puzzle', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle', on_delete=models.CASCADE)),
                ('team', models.ForeignKey(to='huntserver.Team', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Unlockable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.CharField(default=b'TXT', max_length=3, choices=[(b'IMG', b'Image'), (b'PDF', b'PDF'), (b'TXT', b'Text'), (b'WEB', b'Link')])),
                ('content', models.CharField(max_length=500)),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='unlockables',
            field=models.ManyToManyField(to='huntserver.Unlockable', blank=True),
        ),
        migrations.AddField(
            model_name='team',
            name='unlocked',
            field=models.ManyToManyField(related_name='unlocked_for', through='huntserver.Unlock', to='huntserver.Puzzle', blank=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='team',
            field=models.ForeignKey(to='huntserver.Team', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='solve',
            name='submission',
            field=models.ForeignKey(to='huntserver.Submission', blank=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='solve',
            name='team',
            field=models.ForeignKey(to='huntserver.Team', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='person',
            name='teams',
            field=models.ManyToManyField(to='huntserver.Team', blank=True),
        ),
        migrations.AddField(
            model_name='message',
            name='team',
            field=models.ForeignKey(to='huntserver.Team', on_delete=models.CASCADE),
        ),
    ]
