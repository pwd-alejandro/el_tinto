# Generated by Django 4.0.3 on 2022-07-25 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0014_alter_mail_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='tweet',
            field=models.CharField(default='', help_text='229 characters max', max_length=229),
        ),
    ]
