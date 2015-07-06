# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0012_auto_20150704_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle')),
                ('team', models.ForeignKey(to='huntserver.Team')),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='unlocked1',
            field=models.ManyToManyField(related_name='unlocked_for1', through='huntserver.Unlock', to='huntserver.Puzzle', blank=True),
        ),
    ]
