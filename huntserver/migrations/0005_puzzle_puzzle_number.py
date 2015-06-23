# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0004_auto_20150616_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='puzzle_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
