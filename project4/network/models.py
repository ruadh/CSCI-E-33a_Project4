# from django.db.models.aggregates import Count
from django.db.models.fields import CharField
import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.db.models import Max


class User(AbstractUser):
    # The spec did not call for local time zones, but users would expect it, and I already did this in Project 2.
    # Timezones list approach from:  https://stackoverflow.com/a/45867250
    timezones = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(max_length=32, choices=timezones,
                                default=settings.DEFAULT_TIMEZONE)
    following = models.ManyToManyField('User', blank=True, related_name='followers')

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    def __str__(self):
        return f'{self.username}'

    # CITATION:  Adapted from provided models.py in Project 3
    def serialize(self):
        return {
            'id': self.id,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'followers': [user.id for user in self.followers.all()]
        }


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    # content = models.CharField(max_length=256, null=False, blank=False)
    content = models.CharField(max_length=settings.CHARACTER_LIMIT, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    liker = models.ManyToManyField(User, blank=True, related_name='likes')

    def __str__(self):
        return f'{self.author} @ {self.timestamp.strftime("%x %X")}'
   
    # @property
    def likes_count(self):
        return self.liker.count()

    # CITATION:  Adapted from provided models.py in Project 3
    def serialize(self):
        return {
            'id': self.id,
            'author': self.author.username,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%x %X'),
            'likers': [user.id for user in self.liker.all()],
            # TO DO:  Why does this have to be a method, while followers count doesn't?
            'likes_count': self.likes_count()
        }