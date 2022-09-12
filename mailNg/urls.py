from django.urls import path

from . import views

app_name = 'mailNg'

urlpatterns = [
    path("", views.index, name="index"),

    # API Routes
    path("emails/", views.compose, name="compose"),
    path("emails/<int:email_id>/", views.email, name="email"),
    path("emails/username/", views.setUsername, name="username"),
    path("emails/delete", views.delete, name="delete"),
    path("emails/<str:mailbox>/", views.mailbox, name="mailbox"),
]
