# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0010_remove_team_solved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='solved1',
        ),
        migrations.AddField(
            model_name='team',
            name='solved',
            field=models.ManyToManyField(related_name='solved_for', through='huntserver.Solve', to='huntserver.Puzzle', blank=True),
        ),
    ]
