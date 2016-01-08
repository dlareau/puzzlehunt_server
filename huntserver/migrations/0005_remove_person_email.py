# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0004_auto_20151226_0715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='email',
        ),
    ]
