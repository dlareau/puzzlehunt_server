# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0013_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='hunt',
            name='is_current_hunt',
            field=models.NullBooleanField(default=None, unique=True),
        ),
    ]
