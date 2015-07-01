# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0009_auto_20150701_1118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='solved',
        ),
    ]
