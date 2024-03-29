# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-04 20:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0009_auto_20160502_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('location', models.TextField()),
                ('project_name', models.TextField()),
                ('health_topic', models.TextField()),
                ('technology_platform', models.TextField()),
                ('organisation', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
