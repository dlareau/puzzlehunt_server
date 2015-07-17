# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0021_auto_20150717_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unlockable',
            name='content_type',
            field=models.CharField(max_length=3),
        ),
    ]
