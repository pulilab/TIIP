# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-11-29 13:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0030_auto_20171129_1334'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='digitalstrategy',
            options={'verbose_name_plural': 'Digital Strategies'},
        ),
        migrations.AlterModelOptions(
            name='hscchallenge',
            options={'ordering': ['name', 'challenge'], 'verbose_name_plural': 'Health Categories'},
        ),
    ]
