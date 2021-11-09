import json
from django import forms
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from .models import Post, User


# FORM CLASSES

# New post form
class PostForm(forms.ModelForm):
    model = Post
    fields = ['content']
    widgets = {
        'content': forms.Textarea(
                attrs={'placeholder': 'What\'s on your mind?'}),
    }

# Like form

# class LikeForm(forms.ModelForm):
#     class Meta:
#         model = Like
#         fields = ['liker', 'post']
#         widgets = {
#             'liker': forms.HiddenInput,
#             'post': forms.HiddenInput
#         }

# TO DO:  Follow form

# class FollowForm(forms.ModelForm):
#     class Meta:
#         model = Follow
#         fields = ['follower', 'followed']
#         widgets = {
#             'follower': forms.HiddenInput,
#             'followed': forms.HiddenInput
#         }


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

# Display a list of posts

def index(request, title='Recent Posts'):
    # TO DO:  We need to do this with Javascript
    # TO DO:  It should be paginated
    posts = Post.objects.all()
    return render(request, 'network/index.html', {'posts': posts, 'title': title})


# Create a post
# Adapted from 'compose' from the Project 3 starter files

@csrf_exempt
@login_required
def submit_post(request):

    # Make sure the request is a POST
    if request.method != 'POST':
        return JsonResponse({
            'error': 'POST request required.'
            }, status=400)

    # Double-check that the content was provided
    # (JS shouldn't allow submission without it, but just to be safe)
    data = json.loads(request.body)

    # Make sure that there is actual (non-whitespace) content
    content = data.get('content').strip()
    if content == '':
        return JsonResponse({
            'error': 'Content required.'
        }, status=400)

    # Create the post
    post = Post(
            author=request.user,
            content = content
            )
    post.save()

    return JsonResponse({'message': 'Post saved successfully.'}, status=201)


# Like or unlike a post

@login_required
def toggle_like(request):
    like = Like.objects.get(liker=request.user) # Is this going to work?
    # If the user already likes this post, delete the like record
    # Otherwise, create a like record
    pass



# FOLLOWS

@login_required
def toggle_follow(request):
    # If the user already follows the other user, delete the follow record
    # Otherwise, create a follow record
    pass
