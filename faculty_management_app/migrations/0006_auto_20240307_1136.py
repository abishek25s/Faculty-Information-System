# Generated by Django 3.0.7 on 2024-03-07 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0005_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='publication_date',
            field=models.CharField(max_length=255),
        ),
    ]
