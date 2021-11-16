import json
import pytz

from django import forms
from django.db import IntegrityError
# from django.forms.models import InlineForeignKeyField
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Post, User

# TEMP FOR TESTING:  supports adding pauses to API calls
import time


# FORM CLASSES

# New post form


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'placeholder': 'What\'s on your mind?'})
        }


# AUTHENTICATION (provided)


def login_view(request):
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
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
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


# POSTS

# Display the home page with the first page of posts
def index(request):
    posts = Post.objects.all().order_by('-timestamp').all()
    return paginate_posts(request, '', posts, 'Recent Posts')

# Display the posts followed by the current user


@login_required
def following_posts(request):
    # CITATION:  I got help with the syntax from the Django documentation and also https://stackoverflow.com/a/45768219
    posts = Post.objects.filter(
        author__in=request.user.following.all()).order_by('-timestamp').all()
    if posts.count() > 0:
        title = 'Recent Posts by Users I\'m Following'
    else:
        title = 'You are not following any users'
    return paginate_posts(request, '', posts, title )


# Paginate a list of posts
# CITATION:  Adapted from Vancara example project in Vlad's section
def paginate_posts(request, profile, posts, title):
    # Determine the desired page number from the request
    page_num = request.GET.get('page', 1)
    # Create the paginator object
    paginator = Paginator(posts, settings.PAGE_SIZE)
    # Get the specific page's worth of posts
    page = paginator.page(page_num)
    post_form = PostForm()
    return render(request, 'network/index.html', {'page': page, 'profile': profile, 'title': title, 'post_form': post_form})


# Create a post
# NOTE: I opted to handle this with Django instead of JS, since most users will expect to see a refreshed list
#       of current posts with their new post on top after submitting.  (Like and follow would be expected to happen in situ.)

@login_required
def post_add(request):
    # If we're posting data, attempt to process the form
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(
                request, 'Invalid form entry.  Please fix the issues below and resubmit.')
            return render(request, 'network/index.html', {
                'post_form': form
            })
    # It somehow we call this function without posting, load the page with a blank new listing form
    else:
        return render(request, 'network/index.html', {
            'post_form': PostForm()
        })



# PROFILES
def view_profile(request, id):
    # Get the profile details
    try:
        profile = User.objects.get(pk=id)
    # CITATION:  Exception type borrowed from provided views.py in Project 3
    except User.DoesNotExist:
        # TO DO:  
        # If the profile isn't found, show an error instead of loading the profile page
        return HttpResponse('nope!')

    # Get that user's posts  
    posts = Post.objects.filter(author=id).order_by('-timestamp').all()
    # Show the profile page, even if the user has no posts
    return paginate_posts(request, profile, posts, f'Recent Posts by {profile.username}')


# API


# Edit a post

# TO DO:  Remove CSRF exemption
@csrf_exempt
@login_required
def update_post(request, id):

    # TEMP FOR TESTING
    time.sleep(1)

    try:
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)

    # Don't allow users to edit others' posts
    # NOTE:  I'm not 100% sure error 400 is correct, but I chose it based on: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
    if request.user != post.author:
        return JsonResponse({'error': 'You may not edit this post because you are not its author.'}, status=400)

    if request.method == 'PUT':
        # Update the post contents
        post.content = json.loads(request.body).get('content')
        post.save()
        return JsonResponse(post.serialize(), status=200)

    # Update the contents
    return JsonResponse({'error': 'PUT request required.'}, status=400)




# Toggle whether the current user likes or does not like a post
# TO DO:  Add comments about toggle vs. specify action

@login_required
def toggle_like(request, id):

    # TEMP FOR TESTING
    time.sleep(1)

    try:
        post = Post.objects.get(pk=id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found.'}, status=404)

    # Don't allow a user to like their own post
    # NOTE:  I'm not 100% sure error 400 is correct, but I chose it based on: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
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


# Toggle whether the current user likes or does not like a post
# TO DO:  Add comments about toggle vs. specify action

@login_required
def toggle_follow(request, id):

    # TEMP FOR TESTING
    time.sleep(1)

    try:
        profile = User.objects.get(pk=id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=404)

    # Don't allow a user to follow themselves
    # NOTE:  I'm not 100% sure error 400 is correct, but I chose it based on: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
    if request.user == profile:
        return JsonResponse({'error': 'You may not follow yourself.'}, status=400)

    # Toggle the following/not following value
    if request.user in profile.followers.all():
        # Remove the user from the followers
        profile.followers.remove(request.user)
        return JsonResponse(profile.serialize(), status=200)
        # return JsonResponse({'error': 'request.user is in profile.followers.all().'}, status=400)
    else:
        # Add the user to the followers
        profile.followers.add(request.user)
        return JsonResponse(profile.serialize(), status=200)
        # return JsonResponse({'error': 'request.user is NOT in profile.followers.all().'}, status=400)
