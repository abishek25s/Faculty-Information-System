# Generated by Django 3.1.1 on 2024-03-07 14:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0010_auto_20240307_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookchapter',
            name='academic_year',
            field=models.CharField(default=django.utils.timezone.now, max_length=9),
            preserve_default=False,
        ),
    ]
