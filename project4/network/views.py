import json

from django import forms
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import Post, User
# from .models import Post, User, Like, Follow

# TO DO:  MOVE TO SETTINGS
# Set the number of posts per page
PAGE_SIZE = 10

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
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'network/register.html', {
                'message': 'Passwords must match.'
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'network/register.html', {
                'message': 'Username already taken.'
            })
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'network/register.html')


# POSTS

# Display the home page with the first page of posts
def index(request):
    posts = Post.objects.all().order_by('-timestamp').all()
    return paginate_posts(request, '', posts, 'Recent Posts')

# Display the posts followed by the current user


@login_required
def following_posts(request):
    # I got help with the syntax from the Django documentation and also https://stackoverflow.com/a/45768219
    posts = Post.objects.filter(
        author__in=request.user.following.all()).order_by('-timestamp').all()
    return paginate_posts(request, '', posts, 'Recent Posts by Users I\'m Following')


# Paginate a list of posts
# CITATION:  Adapted from Vancara example project in Vlad's section
def paginate_posts(request, profile, posts, title):
    # Determine the desired page number from the request
    page_num = request.GET.get('page', 1)
    # Create the paginator object
    paginator = Paginator(posts, PAGE_SIZE)
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


# Like or unlike a post
# TO DO

@login_required
def toggle_like(request):
    print('function toggle_like')
    # If the user already likes this post, delete the like record
    # Otherwise, create a like record
    # return JsonResponse({'message': 'Like updated successfully.'}, status=201)
    return JsonResponse({'message': 'function toggle_like'}, status=201)


# FOLLOWS

@login_required
def toggle_follow(request):
    # If the user already follows the other user, delete the follow record
    # Otherwise, create a follow record
    pass


# PROFILES
def view_profile(request, id):
    # Get the profile details
    try:
        profile = User.objects.get(pk=id)
    except User.DoesNotExist:
        # TO DO:  
        # If the profile isn't found, show an error instead of loading the profile page
        return HttpResponse('nope!')

    # Get that user's posts  
    posts = Post.objects.filter(author=id).order_by('-timestamp').all()
    # Show the profile page, even if the user has no posts
    return paginate_posts(request, profile, posts, f'Recent Posts by {profile.username}')
