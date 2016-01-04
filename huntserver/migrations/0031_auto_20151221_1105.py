# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0030_auto_20151016_1021'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hunt',
            options={'permissions': (('view_task', 'Can see available tasks'),)},
        ),
    ]
