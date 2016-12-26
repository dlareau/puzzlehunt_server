# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0014_hunt_is_current_hunt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hunt',
            name='is_current_hunt',
            field=models.BooleanField(default=False),
        ),
    ]
