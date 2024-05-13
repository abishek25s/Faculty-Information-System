from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty_management_app', '0031_staffs_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certification',
            name='completion_date',
        ),
        migrations.AddField(
            model_name='certification',
            name='end_date',
            field=models.DateField(auto_now_add=True),  # Set the default value to the current date
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certification',
            name='start_date',
            field=models.DateField(auto_now_add=True),  # Set the default value to the current date
            preserve_default=False,
        ),
    ]