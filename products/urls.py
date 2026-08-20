from django.urls import path

from . import views


app_name = "products"


urlpatterns = [

    # ==================================
    # CUSTOMER STOREFRONT
    # ==================================

    path(
        "",
        views.storefront_product_list,
        name="storefront_product_list",
    ),

    path(
        "<int:pk>/",
        views.storefront_product_detail,
        name="storefront_product_detail",
    ),


    # ==================================
    # PRODUCT MANAGEMENT
    # ==================================

    path(
        "manage/",
        views.product_list,
        name="product_list",
    ),

    path(
        "manage/create/",
        views.product_create,
        name="product_create",
    ),

    path(
        "manage/<int:pk>/",
        views.product_detail,
        name="product_detail",
    ),

    path(
        "manage/<int:pk>/edit/",
        views.product_update,
        name="product_update",
    ),

    path(
        "manage/images/<int:pk>/delete/",
        views.product_image_delete,
        name="product_image_delete",
    ),

    path(
        "manage/<int:pk>/delete/",
        views.product_delete,
        name="product_delete",
    ),

]