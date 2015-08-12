# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0025_remove_team_passphrase'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='objects',
            new_name='unlockables',
        ),
    ]
