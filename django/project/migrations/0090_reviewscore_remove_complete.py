# Generated manually

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0090_reviewscore_remove_complete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewscore',
            name='complete',
        ),
    ]