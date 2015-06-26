# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0007_submission_puzzle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='response_text',
            field=models.CharField(max_length=400, blank=True),
        ),
    ]
