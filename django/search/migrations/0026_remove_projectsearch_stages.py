# Generated by Django 2.1 on 2022-01-21 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0025_projectsearch_partner_names'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectsearch',
            name='stages',
        ),
    ]
