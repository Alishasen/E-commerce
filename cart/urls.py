from django.urls import path
from . import views
app_name = "cart"
urlpatterns = [

    path(
        "",
        views.cart_detail,
        name="cart_detail",
    ),

    path(
        "add/<int:product_id>/",
        views.cart_add,
        name="cart_add",
    ),

    path(
        "update/<int:product_id>/",
        views.cart_update,
        name="cart_update",
    ),

    path(
        "remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove",
    ),

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "payment/esewa/<int:order_id>/",
        views.esewa_payment,
        name="esewa_payment",
    ),

    path(
        "payment/esewa/success/",
        views.esewa_success,
        name="esewa_success",
    ),

    path(
        "payment/esewa/failure/",
        views.esewa_failure,
        name="esewa_failure",
    ),

    path(
        "order/<int:order_id>/",
        views.order_detail,
        name="order_detail",
    ),
        path(
        "payment/success/<int:order_id>/",
        views.payment_success,
        name="payment_success",
    ),
]