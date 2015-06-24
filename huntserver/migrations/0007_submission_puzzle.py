# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0006_auto_20150623_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='puzzle',
            field=models.ForeignKey(default=2, to='huntserver.Puzzle'),
            preserve_default=False,
        ),
    ]
