# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0024_auto_20150809_2104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='passphrase',
        ),
    ]
