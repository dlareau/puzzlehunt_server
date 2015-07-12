# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0017_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='response',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
