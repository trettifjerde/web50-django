from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .views import (
        ListingsView, CategoriesView, WatchlistView, 
        CategoryView, ListingView, MerchantView, 
        ListingCreateView, ListingUpdateView,
        CommentCreateView
)

app_name = 'commerce'

urlpatterns = [
    path('', ListingsView.as_view(), name='index'),
    path("categories/", CategoriesView.as_view(), name="categories"),
    path("categories/<slug>/", CategoryView.as_view(), name="category"),
    path("listing/<int:pk>", ListingView.as_view(), name="listing"),
    path("listing/new", ListingCreateView.as_view(), name="new_listing"),
    path("listing/<int:pk>/edit", ListingUpdateView.as_view(), name="edit_listing"),
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("merchants/<int:pk>/", MerchantView.as_view(), name="merchant"),
    path("profile/", views.profile, name="profile"),

    path("listing/<int:pk>/comment/new/", CommentCreateView.as_view(), name="add_comment"),
    path("bid/", views.bid, name="bid"),
    path("close_listing/", views.close_listing, name="close_listing"),
    path("delete_comment/", views.delete_comment, name="delete_comment"),
    path("watchlist_toggle/", views.watchlist_toggle, name="watchlist_toggle"),
    path("delete_listing/", views.delete_listing, name="delete_listing"),
]

'''
path("", views.index, name="index"),
path("categories", views.categories, name="categories"),
path("watchlist/", views.watchlist, name="watchlist"),
path("category/<slug>/", views.category, name="category"),
'''