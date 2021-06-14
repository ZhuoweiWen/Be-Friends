
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following_page, name="following_page"),
    path("follower_page/<str:username>/<str:follow>", views.follow_page, name="follow_page"),


    #API Routes
    path("posts", views.post, name="post"),
    path("follow", views.follow, name="follow"),
    path("edit", views.edit, name="edit"),
    path("like", views.like, name="like"),
    path("comment", views.comment, name="comment")
]
