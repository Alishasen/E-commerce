from django.urls import path

from . import views


app_name = "wishlist"


urlpatterns = [

    path(
        "",
        views.wishlist_list,
        name="list",
    ),

    path(
        "add/<int:pk>/",
        views.add_to_wishlist,
        name="add",
    ),

    path(
        "remove/<int:pk>/",
        views.remove_from_wishlist,
        name="remove",
    ),

]