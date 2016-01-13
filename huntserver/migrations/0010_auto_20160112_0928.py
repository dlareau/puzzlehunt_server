# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0009_auto_20160104_1317'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='is_andrew_acct',
            new_name='is_shib_acct',
        ),
    ]
