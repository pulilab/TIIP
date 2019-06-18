# Generated by Django 2.0.7 on 2018-07-11 15:01

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0004_auto_20170717_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=models.SET(user.models.UserProfile.get_sentinel_user), to='user.UserProfile'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(null=True, on_delete=models.SET(user.models.UserProfile.get_sentinel_user), to='user.UserProfile'),
        ),
    ]
