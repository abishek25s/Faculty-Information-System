# Generated by Django 4.1.2 on 2024-03-27 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0037_currentexperience_to_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentexperience',
            name='is_relieved',
            field=models.BooleanField(default=False),
        ),
    ]
