# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import huntserver.models


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0019_auto_20171008_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='huntassetfile',
            name='file',
            field=models.FileField(storage=huntserver.models.OverwriteStorage(), upload_to=b'hunt/assets/'),
        ),
    ]
