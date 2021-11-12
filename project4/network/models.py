from django.db.models.aggregates import Count
from django.db.models.fields import CharField
import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max


class User(AbstractUser):
    # The spec did not call for local time zones, but users would expect it, and I already did this in Project 2.
    # Timezones list approach from:  https://stackoverflow.com/a/45867250
    timezones = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(max_length=32, choices=timezones,
                                default=settings.DEFAULT_TIMEZONE)
    following = models.ManyToManyField("User", blank=True, related_name='followers')

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    def __str__(self):
        return f'{self.username}'


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    content = models.CharField(max_length=256, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    liker = models.ManyToManyField(User, blank=True, related_name='likes')

    def __str__(self):
        return f'{self.author} @ {self.timestamp.strftime("%x %X")}'
   
    # @property
    def likes_count(self):
        return self.liker.count()