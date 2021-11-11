
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),


    # API Routes
    path("posts", views.submit_post, name="post"),
    path("posts/<str:page>", views.list_posts, name="list_posts")
]