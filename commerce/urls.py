from django.urls import path

from . import views

app_name = 'commerce'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.commerce_login_view, name="login"),
    path("logout", views.commerce_logout_view, name="logout"),
    path("register", views.commerce_register, name="register"),
    path("profile", views.profile, name="profile"),
    path("categories", views.categories, name="categories"),
    path("category/<slug>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/edit", views.edit_listing, name="edit_listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("close_listing/", views.close_listing, name="close_listing"),
    path("listing/<int:listing_id>/comment/new", views.add_comment, name="add_comment"),
    path("deleteComment/", views.delete_comment, name="delete_comment"),
    path("watchlistToggle/", views.watchlist_toggle, name="watchlist_toggle"),
    path("deleteListing/", views.delete_listing, name="delete_listing"),
    path("merchants/<int:merchant_id>", views.merchant, name="merchant")
]