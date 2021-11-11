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

    @property
    def followers_count(self):
        return self.followers.count()

    def __str__(self):
        return f'{self.username}'


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=256, null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author} @ {self.timestamp.strftime("%x %X")}'
   
    @property
    def likes_count(self):
        return self.likes.count()

    # TO DO:  Do I still need this?
    # CITATION: Adapted from the Project 3 Email model. 
    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes_count": self.likes_count
        }




class Like(models.Model):
    # If the liker or the post is deleted, we should delete the like
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    
    def __str__(self):
        return f'{self.liker} likes {self.post}'


class Follow(models.Model):
    # If the follower or followee is deleted, we should delete the follow
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f'{self.follower} is following {self.followed}'

