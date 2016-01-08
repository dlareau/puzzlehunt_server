# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0003_auto_20151226_0710'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='login_info',
            new_name='user',
        ),
        migrations.RemoveField(
            model_name='person',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='last_name',
        ),
    ]
