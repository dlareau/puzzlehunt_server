# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0005_puzzle_puzzle_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='hunt',
            name='hunt_number',
            field=models.IntegerField(default=0, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='puzzle',
            name='puzzle_id',
            field=models.CharField(default=0, max_length=8),
            preserve_default=False,
        ),
    ]
