# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0008_auto_20150626_1053'),
    ]

    operations = [
        migrations.CreateModel(
            name='Solve',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle')),
                ('submission', models.ForeignKey(to='huntserver.Submission', blank=True)),
                ('team', models.ForeignKey(to='huntserver.Team')),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='solved1',
            field=models.ManyToManyField(related_name='solved_for1', through='huntserver.Solve', to='huntserver.Puzzle', blank=True),
        ),
    ]
