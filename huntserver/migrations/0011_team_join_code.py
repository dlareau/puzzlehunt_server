# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0010_auto_20160112_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='join_code',
            field=models.CharField(default='FFFFF', max_length=5),
            preserve_default=False,
        ),
    ]
