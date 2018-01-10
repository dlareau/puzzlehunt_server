# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0018_auto_20171008_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hunt',
            name='template',
            field=models.TextField(default=b''),
        ),
    ]
