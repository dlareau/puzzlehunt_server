# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0013_auto_20150705_1843'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='unlocked',
        ),
    ]
