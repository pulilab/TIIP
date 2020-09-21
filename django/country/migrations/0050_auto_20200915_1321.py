# Generated by Django 2.1 on 2020-09-15 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0049_auto_20200901_1535'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='countryoffice',
            options={'verbose_name': 'UNICEF Office', 'verbose_name_plural': 'UNICEF Offices'},
        ),
        migrations.AlterModelOptions(
            name='currency',
            options={'verbose_name_plural': 'Currencies'},
        ),
        migrations.AlterField(
            model_name='countryoffice',
            name='regional_office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='country.RegionalOffice'),
        ),
    ]
