# Generated by Django 4.2.2 on 2023-07-09 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_contributor_project_alter_contributor_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
