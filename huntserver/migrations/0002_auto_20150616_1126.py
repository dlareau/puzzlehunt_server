# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzle',
            name='unlocks',
            field=models.ManyToManyField(related_name='unlocks_rel_+', to='huntserver.Puzzle', blank=True),
        ),
    ]
