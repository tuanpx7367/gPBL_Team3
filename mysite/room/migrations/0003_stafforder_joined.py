# Generated by Django 4.1.3 on 2022-11-25 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_stafforder_delete_stafflistorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='stafforder',
            name='joined',
            field=models.BooleanField(default=False),
        ),
    ]
