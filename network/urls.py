
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'network'

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new, name="new"),
    path("user/<int:user_id>", views.user, name="user"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path('following/', views.following, name="following"),
    path('like/', views.like, name='like'),
    path('avatar/', views.avatar, name='avatar'),
    path('unload/', views.delete_avatar, name='delete_avatar')
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
