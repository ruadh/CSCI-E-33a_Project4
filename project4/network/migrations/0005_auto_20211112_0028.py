# Generated by Django 3.2.9 on 2021-11-12 00:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_auto_20211111_2347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='follower',
        ),
        migrations.AddField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL),
        ),
    ]
