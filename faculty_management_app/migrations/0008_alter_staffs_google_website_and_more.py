# Generated by Django 4.1.2 on 2024-03-07 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0007_remove_staffs_aadhar_set_remove_staffs_pan_set_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffs',
            name='google_website',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='scopus_website',
            field=models.URLField(),
        ),
    ]
