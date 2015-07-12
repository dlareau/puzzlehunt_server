# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0018_message_response'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='response',
            new_name='is_response',
        ),
    ]
