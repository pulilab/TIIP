# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-04 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0011_auto_20170503_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countryfield',
            name='enabled',
            field=models.BooleanField(default=True, help_text='This field will show up on the project page if enabled'),
        ),
        migrations.AlterField(
            model_name='countryfield',
            name='question',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='countryfield',
            name='type',
            field=models.IntegerField(choices=[(1, 'Text field'), (2, 'Numeric field'), (3, 'Yes - no field')]),
        ),
    ]
