from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_page", views.create_page, name="createPage"),
    path("create", views.create, name="create"),
    path("listing_page/<int:id>", views.listing_page, name="listingPage"),
    path("addWatchlist/<int:id>", views.add_watchlist, name="addWatchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("removeWatchlist/<int:id>", views.remove_watchlist, name="removeWatchlist"),
    path("addBid<int:id>", views.add_bid, name="addBid"),
    path("closeListing<int:id>", views.close_auction, name="closeListing"),
    path("category_page<str:category>", views.category_page, name="categoryPage"),
    path("addComment/<int:id>", views.add_comment, name="addComment"),
    path("remoweWatclistPage<int:id>", views.watchlist_remowe, name="watchlistPage")
]
