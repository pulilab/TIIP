# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-01-04 13:28
from __future__ import unicode_literals

from django.db import migrations


def create_project_admins(apps, schema_editor):
    Project = apps.get_model('project', 'Project')
    ProjectApproval = apps.get_model('project', 'ProjectApproval')

    for project in Project.projects.filter(approval__isnull=True):
        ProjectApproval.objects.create(project=project)


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0045_projectimport'),
    ]

    operations = [
        migrations.RunPython(create_project_admins, migrations.RunPython.noop),
    ]
