# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0003_auto_20150616_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='unlocked',
            field=models.ManyToManyField(related_name='unlocked_for', to='huntserver.Puzzle', blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='solved',
            field=models.ManyToManyField(related_name='solved_for', to='huntserver.Puzzle', blank=True),
        ),
    ]
