# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0011_auto_20150701_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='puzzle_id',
            field=models.CharField(unique=True, max_length=8),
        ),
    ]
