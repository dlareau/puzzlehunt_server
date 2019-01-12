# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sys

def printHelp(apps, schema_editor):
    if 'test' not in sys.argv:
        print("=== NOTICE: ===")
        print("Do not forget to add the line")
        print("'OPTIONS': {'charset': 'utf8mb4'},")
        print("to your database settings if applying this")
        print("migration to an existing database/server.")
        print("===============")

class Migration(migrations.Migration):

    dependencies = [
        ('huntserver', '0021_auto_20180402_2224'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                'ALTER TABLE `auth_user` MODIFY `password` varchar(128) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `auth_user` MODIFY `username` varchar(30) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `auth_user` MODIFY `first_name` varchar(30) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `auth_user` MODIFY `last_name` varchar(30) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `auth_user` MODIFY `email` varchar(254) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `django_admin_log` MODIFY `object_id` longtext CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `django_admin_log` MODIFY `object_repr` varchar(200) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `django_admin_log` MODIFY `change_message` longtext CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_hunt` MODIFY `hunt_name` varchar(200) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_hunt` MODIFY `location` varchar(100) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_hunt` MODIFY `template` longtext CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_huntassetfile` MODIFY `file` varchar(100) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_message` MODIFY `text` varchar(400) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_person` MODIFY `phone` varchar(20) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_person` MODIFY `comments` varchar(400) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_person` MODIFY `allergies` varchar(400) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `puzzle_name` varchar(200) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `puzzle_id` varchar(8) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `answer` varchar(100) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `link` varchar(200) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_response` MODIFY `regex` varchar(400) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_response` MODIFY `text` varchar(400) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_submission` MODIFY `submission_text` varchar(100) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_submission` MODIFY `response_text` varchar(400) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_team` MODIFY `team_name` varchar(200) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_team` MODIFY `location` varchar(80) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_team` MODIFY `join_code` varchar(5) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_unlockable` MODIFY `content_type` varchar(3) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
                'ALTER TABLE `huntserver_unlockable` MODIFY `content` varchar(500) CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci ',
            ],
            reverse_sql=[
                'ALTER TABLE `auth_user` MODIFY `password` varchar(128) ',
                'ALTER TABLE `auth_user` MODIFY `username` varchar(30) ',
                'ALTER TABLE `auth_user` MODIFY `first_name` varchar(30) ',
                'ALTER TABLE `auth_user` MODIFY `last_name` varchar(30) ',
                'ALTER TABLE `auth_user` MODIFY `email` varchar(254) ',
                'ALTER TABLE `django_admin_log` MODIFY `object_id` longtext ',
                'ALTER TABLE `django_admin_log` MODIFY `object_repr` varchar(200) ',
                'ALTER TABLE `django_admin_log` MODIFY `change_message` longtext ',
                'ALTER TABLE `huntserver_hunt` MODIFY `hunt_name` varchar(200) ',
                'ALTER TABLE `huntserver_hunt` MODIFY `location` varchar(100) ',
                'ALTER TABLE `huntserver_hunt` MODIFY `template` longtext ',
                'ALTER TABLE `huntserver_huntassetfile` MODIFY `file` varchar(100) ',
                'ALTER TABLE `huntserver_message` MODIFY `text` varchar(400) ',
                'ALTER TABLE `huntserver_person` MODIFY `phone` varchar(20) ',
                'ALTER TABLE `huntserver_person` MODIFY `comments` varchar(400) ',
                'ALTER TABLE `huntserver_person` MODIFY `allergies` varchar(400) ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `puzzle_name` varchar(200) ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `puzzle_id` varchar(8) ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `answer` varchar(100) ',
                'ALTER TABLE `huntserver_puzzle` MODIFY `link` varchar(200) ',
                'ALTER TABLE `huntserver_response` MODIFY `regex` varchar(400) ',
                'ALTER TABLE `huntserver_response` MODIFY `text` varchar(400) ',
                'ALTER TABLE `huntserver_submission` MODIFY `submission_text` varchar(100) ',
                'ALTER TABLE `huntserver_submission` MODIFY `response_text` varchar(400) ',
                'ALTER TABLE `huntserver_team` MODIFY `team_name` varchar(200) ',
                'ALTER TABLE `huntserver_team` MODIFY `location` varchar(80) ',
                'ALTER TABLE `huntserver_team` MODIFY `join_code` varchar(5) ',
                'ALTER TABLE `huntserver_unlockable` MODIFY `content_type` varchar(3) ',
                'ALTER TABLE `huntserver_unlockable` MODIFY `content` varchar(500) ',
            ]
        ),
        migrations.RunPython(printHelp),
    ]
