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

from .models import Post, User, Like, Follow

# TO DO:  MOVE TO SETTINGS
# Set the number of posts per page
PAGE_SIZE=5

# FORM CLASSES

# New post form
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                    attrs={'placeholder': 'What\'s on your mind?'}),
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
    return list_posts(request, posts, 'Recent Posts', show_form=True)


# API:  Return a specific page's worth of posts
# CITATION:  Adapted from Vancara example project in Vlad's section
# TO DO:  Figure out what show-form is
def list_posts(request, posts, title, show_form):
    # Determine the desired page number from the request
    page_num = request.GET.get('page', 1)
    # Create the paginator object
    paginator = Paginator(posts, PAGE_SIZE)
    # Get the specific page's worth of posts
    page = paginator.page(page_num)
    post_form = PostForm()
    return render(request, 'network/index.html', {'page': page, 'title':title, 'show_form': show_form, 'post_form': post_form})


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
    # like = Like.objects.get(liker=request.user) # Is this going to work?
    # print(like.length)
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
