# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0014_remove_team_unlocked'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='unlocked1',
        ),
        migrations.AddField(
            model_name='team',
            name='unlocked',
            field=models.ManyToManyField(related_name='unlocked_for', through='huntserver.Unlock', to='huntserver.Puzzle', blank=True),
        ),
    ]
