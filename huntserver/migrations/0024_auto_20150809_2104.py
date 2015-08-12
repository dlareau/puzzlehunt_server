# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0023_auto_20150717_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='year',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='team',
            name='passphrase',
            field=models.CharField(default='wrongbaa', max_length=40),
            preserve_default=False,
        ),
    ]
