# Generated by Django 2.1.4 on 2019-01-19 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nav', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='site',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='site',
            name='url',
            field=models.URLField(default=''),
        ),
    ]