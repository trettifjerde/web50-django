
from django.urls import path

from . import views

app_name = 'network'

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new, name="new"),
    path("user/<int:user_id>", views.user, name="user"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path('following/', views.following, name="following"),
    path('like/', views.like, name='like')
]
