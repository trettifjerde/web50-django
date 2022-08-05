from django.urls import path

from . import views

app_name = 'mail'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.mail_login_view, name="login"),
    path("logout", views.mail_logout_view, name="logout"),
    path("register", views.mail_register, name="register"),

    # API Routes
    path("emails/", views.compose, name="compose"),
    path("emails/<int:email_id>", views.email, name="email"),
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
]
