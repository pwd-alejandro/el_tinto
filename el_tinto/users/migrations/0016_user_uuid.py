# Generated by Django 4.0.3 on 2023-05-29 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_remove_user_date_time_remove_user_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=''),
        ),
    ]
