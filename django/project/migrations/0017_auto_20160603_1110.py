# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-03 11:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0016_auto_20160601_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='team',
            field=models.ManyToManyField(blank=True, related_name='team', to='user.UserProfile'),
        ),
        migrations.AlterField(
            model_name='project',
            name='viewers',
            field=models.ManyToManyField(blank=True, related_name='viewers', to='user.UserProfile'),
        ),
    ]
