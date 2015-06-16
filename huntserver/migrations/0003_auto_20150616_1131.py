# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0002_auto_20150616_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='unlocks',
            field=models.ManyToManyField(to='huntserver.Puzzle', blank=True),
        ),
    ]
