# Generated by Django 4.2.2 on 2023-07-07 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=2000)),
                ('type', models.CharField(choices=[('FRONT', 'front-end'), ('BACK', 'back-end'), ('ANDROID', 'android'), ('IOS', 'IOS')], default='FRONT', max_length=10)),
            ],
        ),
    ]