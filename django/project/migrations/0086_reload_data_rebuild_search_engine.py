# Generated by Django 2.1 on 2020-12-11 14:39
from django.core.management import call_command
from django.db import migrations


def add_taxonomies(apps, schema_editor):
    call_command('add_taxonomies', '--verbosity', 0)


def rebuild_search(apps, schema_editor):
    call_command('rebuild_search')


def reorder_stages(apps, schema_editor):
    Stage = apps.get_model('project', 'Stage')
    order = 0
    for item in Stage.objects.all():
        order += 1
        item.order = order
        item.save()


class Migration(migrations.Migration):
    dependencies = [
        ('project', '0085_auto_20201211_1433'),
    ]

    operations = [
        migrations.RunPython(add_taxonomies),
        migrations.RunPython(rebuild_search),
        migrations.RunPython(reorder_stages),
    ]