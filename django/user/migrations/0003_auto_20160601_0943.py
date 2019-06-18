# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-01 09:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def migrate_organisation_names_to_entities(apps, schema_editor):
    UserProfile = apps.get_model("user", "UserProfile")
    Organisation = apps.get_model("user", "Organisation")
    profiles_to_migrate = UserProfile.objects.all()
    for profile in profiles_to_migrate:
        org_name = profile.organisation
        org, _ = Organisation.objects.get_or_create(name=org_name)
        profile.organisation_fk = org
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20160428_0952'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='organisation_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.Organisation'),
        ),
        migrations.RunPython(migrate_organisation_names_to_entities),
    ]
