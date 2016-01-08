# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0005_remove_person_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='andrewid',
        ),
        migrations.AddField(
            model_name='person',
            name='is_andrew_acct',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
