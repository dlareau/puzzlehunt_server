# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0027_hunt_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='hunt',
            name='team_size',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
    ]
