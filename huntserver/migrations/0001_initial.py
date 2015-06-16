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
                ('start_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('comments', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='Puzzle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puzzle_name', models.CharField(max_length=200)),
                ('answer', models.CharField(max_length=100)),
                ('link', models.URLField()),
                ('num_required_to_unlock', models.IntegerField(default=1)),
                ('hunt', models.ForeignKey(to='huntserver.Hunt')),
                ('unlocks', models.ManyToManyField(related_name='unlocks_rel_+', to='huntserver.Puzzle')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submission_time', models.DateTimeField()),
                ('submission_text', models.CharField(max_length=100)),
                ('response_text', models.CharField(max_length=400)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('team_name', models.CharField(max_length=200)),
                ('hunt', models.ForeignKey(to='huntserver.Hunt')),
                ('login_info', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('solved', models.ManyToManyField(to='huntserver.Puzzle')),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='team',
            field=models.ForeignKey(to='huntserver.Team'),
        ),
        migrations.AddField(
            model_name='person',
            name='team',
            field=models.ForeignKey(to='huntserver.Team'),
        ),
    ]
