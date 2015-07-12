# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0019_auto_20150711_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='login_info',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
