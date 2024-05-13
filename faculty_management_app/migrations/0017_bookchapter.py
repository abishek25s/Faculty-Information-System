# Generated by Django 4.1.2 on 2024-03-09 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0016_auto_20240308_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookChapter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('author_name', models.CharField(max_length=100)),
                ('book_chapter_title', models.CharField(max_length=200)),
                ('publisher_name', models.CharField(max_length=100)),
                ('isbn_no', models.CharField(max_length=20)),
                ('month_year_publication', models.CharField(max_length=255)),
                ('doi_if', models.CharField(max_length=255)),
                ('is_scopus_indexed', models.BooleanField(default=False)),
                ('paper_link', models.URLField()),
                ('affiliating_institution_same', models.BooleanField(default=True)),
                ('scopus_link', models.URLField()),
                ('academic_year', models.CharField(blank=True, max_length=9, null=True)),
                ('staff_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='faculty_management_app.staffs')),
            ],
        ),
    ]
