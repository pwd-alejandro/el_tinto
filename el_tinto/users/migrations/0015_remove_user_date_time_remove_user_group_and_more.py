# Generated by Django 4.0.3 on 2023-04-21 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_user_date_time_user_group_user_i_user_invite_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='date_time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='group',
        ),
        migrations.RemoveField(
            model_name='user',
            name='i',
        ),
        migrations.RemoveField(
            model_name='user',
            name='invite',
        ),
        migrations.RemoveField(
            model_name='user',
            name='size_group',
        ),
    ]
