# Generated by Django 3.1.1 on 2024-03-07 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0012_remove_bookchapter_academic_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookchapter',
            name='academic_year',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
    ]
