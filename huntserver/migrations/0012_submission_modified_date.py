# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0011_team_join_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='modified_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 19, 22, 32, 7, 46283, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
