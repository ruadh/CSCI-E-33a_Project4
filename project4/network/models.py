"""Models for the Django Network app"""

import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A class for system users"""
    # The spec did not call for local time zones, but users would expect it, and I already did this in Project 2.
    # Timezones list approach from:  https://stackoverflow.com/a/45867250
    timezones = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    timezone = models.CharField(max_length=32, choices=timezones,
                                default=settings.DEFAULT_TIMEZONE)
    following = models.ManyToManyField('User', blank=True, related_name='followers')

    @property
    def following_count(self):
        """Returns the number of people the current user is following"""
        return self.following.count()

    def __str__(self):
        """Returns the username of the current user"""
        return f'{self.username}'

    # CITATION:     Adapted from provided models.py in Project 3
    # DESIGN NOTE:  The followers list is not needed at this time, so I am only passing the count.
    #               It could be added to the JSON object later if needed.
    def serialize(self):
        """Returns a JSON object containing the user's followers list and following stats"""
        return {
            'id': self.id,
            'following_count': self.following_count,
            'followers': [user.id for user in self.followers.all()]
        }


class Post(models.Model):
    """A class for network posts"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    content = models.CharField(max_length=settings.CHARACTER_LIMIT, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    liker = models.ManyToManyField(User, blank=True, related_name='likes')

    def __str__(self):
        """Returns the post's author and timestamp"""
        return f'{self.author} @ {self.timestamp.strftime("%x %X")}'

    # CITATION:  Adapted from provided models.py in Project 3
    def serialize(self):
        """Returns a JSOn object containing the post's contents, metadata, and likers list"""
        return {
            'id': self.id,
            'author': self.author.username,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%x %X'),
            'likers': [user.id for user in self.liker.all()]
        }
