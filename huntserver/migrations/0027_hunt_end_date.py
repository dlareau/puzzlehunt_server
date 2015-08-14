# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0026_auto_20150811_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='hunt',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 14, 19, 48, 32, 848821, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
