"""Python code for the Django Network app"""

# CITATION:     Import sorting by iSort, as recommended by the Django contributors documentation:
#               https://github.com/PyCQA/isort#readme

import json
# TEMP FOR TESTING:
import time

import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import Post, User


# AUTHENTICATION
# NOTE:  These have been modified slightly from the provided starter file

def login_view(request):
    """Log in the user"""

    if request.method == 'POST':

        # Attempt to sign user in
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            # Set the display timezone to the user's chosen time
            timezone.activate(user.timezone)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'network/login.html', {
                'message': 'Invalid username and/or password.'
            })
    else:
        return render(request, 'network/login.html')


def logout_view(request):
    """Log out the user"""

    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    """Register a new user"""

    # Gather a list of timezones to populate the timezone choice field in the form
    timezones = pytz.common_timezones

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'network/register.html', {
                'message': 'Passwords must match.',
                'timezones': timezones,
                'default_timezone': settings.DEFAULT_TIMEZONE
            })
        if password == '':
            messages.error(request, 'Password cannot be blank')
            return render(request, 'auctions/register.html', {
                'timezones': timezones,
                'default_timezone': settings.DEFAULT_TIMEZONE
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.timezone = request.POST['user_timezone']
            user.save()
        except IntegrityError:
            return render(request, 'network/register.html', {
                'message': 'Username already taken.',
                'timezones': timezones,
                'default_timezone': settings.DEFAULT_TIMEZONE
            })
        login(request, user)
        # Set the display timezone to the user's chosen time
        timezone.activate(user.timezone)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'network/register.html', {
            'timezones': timezones,
            'default_timezone': settings.DEFAULT_TIMEZONE
        })


# PAGES

def index(request):
    """Display the home page with the most recent posts by all users"""

    posts = Post.objects.all().order_by('-timestamp').all()
    return paginate_posts(request, None, posts, 'Recent Posts', None, True)


def paginate_posts(request, profile, posts, title, message=None, show_form=False):
    """Paginate and display the provided list of posts"""
    # CITATION:  Adapted from Vancara example project in Vlad's section

    # Make sure there are posts before we try to paginate them
    if posts is None:
        page = None
    else:
        # Determine the desired page number from the request
        page_num = request.GET.get('page', 1)
        # Create the paginator object
        paginator = Paginator(posts, settings.PAGE_SIZE)
        # Get the specific page's worth of posts
        page = paginator.page(page_num)
    return render(request, 'network/index.html', {
        'page': page,
        'profile': profile,
        'title': title,
        'message': message,
        'show_form': show_form
    })


@login_required
def following_posts(request):
    """Display posts by authors followed by the current user"""

    # CITATION:  I got help syntax help from the Django documentation and also https://stackoverflow.com/a/45768219
    posts = Post.objects.filter(
        author__in=request.user.following.all()).order_by('-timestamp').all()
    if posts.count() > 0:
        title = 'Recent Posts by Users I\'m Following'
    else:
        # Since we're
        title = 'You are not following any users'
    return paginate_posts(request, None, posts, title)


def view_profile(request, id):
    """Display the profile page for a single user"""
    # Get the profile details
    try:
        profile = User.objects.get(pk=id)
    # CITATION:  Exception type borrowed from provided views.py in Project 3
    except User.DoesNotExist:
        # Show a persistent error
        return paginate_posts(request, None, None, '', f'User {id} Not Found')

    # Get that user's posts
    posts = Post.objects.filter(author=id).order_by('-timestamp').all()
    # Show the profile page, even if the user has no posts
    return paginate_posts(request, profile, posts, f'Recent Posts by {profile.username}')


# API METHODS


@login_required
def save_post(request, id=None):
    """Create or edit a post"""

    # TEMP FOR TESTING
    time.sleep(1)

    # Validate the content  (also checked on the frontend, but just to be safe)
    content = json.loads(request.body).get('content').strip()
    if len(content) == 0:
        return JsonResponse({'error': 'Empty posts are not allowed.'}, status=400)
    if len(content) > 256:
        return JsonResponse({'error': f'Posts may not exceed {settings.CHARACTER_LIMIT} characters.'}, status=400)

    # CITATION:  Adapted from compose function in provided views.py from Project 3
    if request.method == 'POST':
        post = Post(
            author=request.user,
            content=content
        )
        post.save()
        return JsonResponse({'message': 'Post created successfully.'}, status=201)
    elif request.method == 'PUT':
        try:
            post = Post.objects.get(pk=id)
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found.'}, status=404)

        # Don't allow users to edit others' posts
        # NOTE:  I'm not sure error 400 is correct, but I chose it based on: https://mzl.la/3kNTYCN
        if request.user != post.author:
            return JsonResponse({'error': 'You may not edit this post because you are not its author.'}, status=400)

        # Update the post contents and save it
        post.content = content
        post.save()
        return JsonResponse(post.serialize(), status=200)

    # Update the contents
    return JsonResponse({'error': 'PUT request required.'}, status=400)


@login_required
def toggle_like(request, id):
    """Toggle whether the current user likes or doesn't like a post"""
    # NOTE: See design notes in toggleLike in network.js for thoughts on toggling the value vs. passing the action

    # TEMP FOR TESTING
    time.sleep(1)

    try:
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)

    # Don't allow a user to like their own post
    if request.user == post.author:
        return JsonResponse({'error': 'You may not like your own post.'}, status=400)

    # Toggle the liked/unliked value
    if request.user in post.liker.all():
        # Remove the user from the likers
        post.liker.remove(request.user)
        return JsonResponse(post.serialize(), status=200)
    else:
        # Add the user to the likers
        post.liker.add(request.user)
        return JsonResponse(post.serialize(), status=200)


@login_required
def toggle_follow(request, id):
    """Toggle whether the current user follows or doesn't follow another user"""
    # NOTE:  See design notes in toggleLike in network.js for thoughts on toggling the value vs. passing the action

    # TEMP FOR TESTING
    time.sleep(1)

    try:
        profile = User.objects.get(pk=id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=404)

    # Don't allow a user to follow themselves
    if request.user == profile:
        return JsonResponse({'error': 'You may not follow yourself.'}, status=400)

    # Toggle the following/not following value
    if request.user in profile.followers.all():
        # Remove the user from the followers
        profile.followers.remove(request.user)
        return JsonResponse(profile.serialize(), status=200)
    else:
        # Add the user to the followers
        profile.followers.add(request.user)
        return JsonResponse(profile.serialize(), status=200)
