# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0022_auto_20150717_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unlockable',
            name='content_type',
            field=models.CharField(default=b'TXT', max_length=3, choices=[(b'IMG', b'Image'), (b'PDF', b'PDF'), (b'TXT', b'Text'), (b'WEB', b'Link')]),
        ),
    ]
