# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0002_puzzle_num_pages'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='year',
        ),
        migrations.AddField(
            model_name='person',
            name='andrewid',
            field=models.CharField(max_length=8, blank=True),
        ),
    ]
