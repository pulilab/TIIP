# Generated by Django 2.1 on 2020-10-26 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0078_project_favorited_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='description',
            field=models.CharField(max_length=1000),
        ),
    ]
