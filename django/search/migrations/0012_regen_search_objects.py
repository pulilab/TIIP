# Generated by Django 2.1 on 2018-08-06 14:02

from django.db import migrations


def regenerate_search_objects(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0011_auto_20180806_1129'),
    ]

    operations = [
        migrations.RunPython(regenerate_search_objects, reverse_code=migrations.RunPython.noop)
    ]
