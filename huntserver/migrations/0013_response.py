# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0012_submission_modified_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('regex', models.CharField(max_length=400)),
                ('text', models.CharField(max_length=400)),
                ('puzzle', models.ForeignKey(to='huntserver.Puzzle')),
            ],
        ),
    ]
