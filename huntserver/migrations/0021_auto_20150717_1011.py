# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0020_auto_20150712_1237'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unlockable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', models.CharField(max_length=40)),
                ('content', models.CharField(max_length=500)),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle')),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='objects',
            field=models.ManyToManyField(to='huntserver.Unlockable', blank=True),
        ),
    ]
