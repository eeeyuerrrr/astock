# Generated by Django 2.1.4 on 2019-01-20 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nav', '0002_auto_20190119_2245'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='category',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='site',
            name='order',
            field=models.IntegerField(default=100),
        ),
    ]
