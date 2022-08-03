from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("new/", views.new, name="new"),
    path("random/", views.random, name="random"),
    path("404/<str:title>", views.not_found, name="404"),
    path("<str:title>", views.entry, name="entry"),
    path("<str:title>/edit", views.edit, name="edit"),
    path("<str:title>/delete", views.delete, name="delete"),
]
