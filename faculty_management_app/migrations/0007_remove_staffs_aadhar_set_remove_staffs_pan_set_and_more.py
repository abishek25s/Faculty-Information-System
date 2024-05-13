# Generated by Django 4.1.2 on 2024-03-07 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0006_auto_20240307_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staffs',
            name='aadhar_set',
        ),
        migrations.RemoveField(
            model_name='staffs',
            name='pan_set',
        ),
        migrations.AddField(
            model_name='staffs',
            name='google_website',
            field=models.URLField(default='http://www.example.com'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='phone',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='staffs',
            name='scopus_website',
            field=models.URLField(default='http://www.example.com'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]