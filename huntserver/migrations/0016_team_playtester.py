# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0015_auto_20161226_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='playtester',
            field=models.BooleanField(default=False),
        ),
    ]
