# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0008_hunt_location'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='solve',
            unique_together=set([('puzzle', 'team')]),
        ),
        migrations.AlterUniqueTogether(
            name='unlock',
            unique_together=set([('puzzle', 'team')]),
        ),
    ]
