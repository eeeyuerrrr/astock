# Generated by Django 2.1.4 on 2019-01-15 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20190113_1755'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='key_expires',
            new_name='activate_key_expires',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='reset_pw_key',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='reset_pw_key_expires',
            field=models.DateTimeField(null=True),
        ),
    ]
