# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0017_auto_20170707_1000'),
    ]

    operations = [
        migrations.CreateModel(
            name='HuntAssetFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'hunt/assets/')),
            ],
        ),
        migrations.AddField(
            model_name='hunt',
            name='template',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
