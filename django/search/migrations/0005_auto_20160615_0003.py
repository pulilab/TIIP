# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-15 00:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_auto_20160606_1456'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectsearch',
            old_name='intervention_areas',
            new_name='health_focus_areas',
        ),
    ]
