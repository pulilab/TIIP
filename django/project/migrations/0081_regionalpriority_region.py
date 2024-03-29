# Generated by Django 2.1 on 2020-12-01 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0080_auto_20201112_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='regionalpriority',
            name='region',
            field=models.IntegerField(blank=True, choices=[(0, 'EAPR'), (1, 'ECAR'), (2, 'ESAR'), (3, 'LACR'), (4, 'MENA'), (5, 'SAR'), (6, 'WCAR'), (7, 'HQ')], null=True),
        ),
    ]
