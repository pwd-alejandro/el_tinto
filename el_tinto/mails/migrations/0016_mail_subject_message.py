# Generated by Django 4.0.3 on 2022-09-13 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0015_alter_mail_tweet'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='subject_message',
            field=models.CharField(default='', help_text='Texto que acompaña al subject', max_length=128),
        ),
    ]
