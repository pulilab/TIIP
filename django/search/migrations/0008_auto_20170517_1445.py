# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-17 14:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_remove_projectsearch_technology_platform'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectsearch',
            name='health_topic',
        ),
        migrations.AddField(
            model_name='projectsearch',
            name='platforms',
            field=models.TextField(blank=True),
        ),
    ]
