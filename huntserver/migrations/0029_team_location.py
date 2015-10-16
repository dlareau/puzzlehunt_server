# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0028_hunt_team_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='location',
            field=models.CharField(default='N/A', max_length=80),
            preserve_default=False,
        ),
    ]
