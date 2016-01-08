# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0006_auto_20160102_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='allergies',
            field=models.CharField(max_length=400, blank=True),
        ),
    ]
