# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0029_team_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='location',
            field=models.CharField(max_length=80, blank=True),
        ),
    ]
