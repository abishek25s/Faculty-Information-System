# Generated by Django 3.1.1 on 2024-03-08 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0015_merge_20240308_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='copyright',
            name='staff_id',
        ),
        migrations.DeleteModel(
            name='BookChapter',
        ),
        migrations.DeleteModel(
            name='Copyright',
        ),
    ]