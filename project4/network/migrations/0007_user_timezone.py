# Generated by Django 3.2.9 on 2021-11-15 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_remove_user_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.CharField(default='America/New_York', max_length=32),
        ),
    ]