# Generated by Django 2.1 on 2020-12-01 10:12

from django.db import migrations, models
import django.db.models.manager
import project.cache


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0081_regionalpriority_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='InnovationWay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name_plural': 'Innovation Ways',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(project.cache.InvalidateCacheMixin, models.Model),
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ISC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=512)),
            ],
            options={
                'verbose_name_plural': 'Information Security Classification',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(project.cache.InvalidateCacheMixin, models.Model),
            managers=[
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
