
from django.urls import path

from . import views

urlpatterns = [
    # Authentication
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),


    # Navigation
    path("", views.index, name="index"),
    path("posts", views.post_add, name="post_add"),
    path("following", views.following_posts, name="following"),
    path("users/<int:id>", views.view_profile, name="view_profile")
]