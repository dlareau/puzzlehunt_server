# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0015_auto_20150705_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='comments',
            field=models.CharField(max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='team',
            field=models.ForeignKey(to='huntserver.Team', blank=True),
        ),
    ]
