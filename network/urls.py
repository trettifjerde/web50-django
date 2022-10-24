
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'network'

urlpatterns = [
    path("", views.index, name="index"),
    path("user/<int:user_id>/", views.user, name="user"),
    path('feed/', views.feed, name="feed"),
    #api
    path("new/", views.new, name="new"),
    path("morePosts/", views.get_more_posts, name="get_more_posts"),
    path("getPost/", views.get_post, name="get_post"),
    path("editPost/", views.edit_post, name="edit_post"),
    path("deletePost/", views.delete_post, name="delete_post"),
    path("follow/", views.follow, name="follow"),
    path('like/', views.like, name='like'),
    path('avatar/', views.avatar, name='avatar'),
    path('unload/', views.delete_avatar, name='delete_avatar')
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
