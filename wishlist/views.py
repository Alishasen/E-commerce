from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product
from .models import Wishlist


@login_required
def add_to_wishlist(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    return redirect(
        "products:storefront_product_detail",
        pk=product.pk,
    )


@login_required
def remove_from_wishlist(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk,
    )

    Wishlist.objects.filter(
        user=request.user,
        product=product,
    ).delete()

    return redirect(
        "products:storefront_product_detail",
        pk=product.pk,
    )


@login_required
def wishlist_list(request):

    wishlist_items = (
        Wishlist.objects
        .filter(user=request.user)
        .select_related("product")
        .prefetch_related("product__images")
    )

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "wishlist_items": wishlist_items,
        },
    )
