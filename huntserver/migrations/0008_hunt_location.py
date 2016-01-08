# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0007_person_allergies'),
    ]

    operations = [
        migrations.AddField(
            model_name='hunt',
            name='location',
            field=models.CharField(default='Porter Hall 100', max_length=100),
            preserve_default=False,
        ),
    ]
