from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from products.models import Product
def cart_count(request):
    cart = request.session.get("cart", {})

    return sum(cart.values())

def cart_detail(request):

    cart = request.session.get("cart", {})

    cart_items = []

    total = 0

    for product_id, quantity in cart.items():

        product = get_object_or_404(
            Product,
            pk=product_id,
        )

        subtotal = product.price * quantity

        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    context = {
        "cart_items": cart_items,
        "total": total,
    }

    return render(
        request,
        "cart/cart_detail.html",
        context,
    )

@login_required(login_url="accounts:login")
def cart_add(request, product_id):

    if request.method != "POST":
        return redirect(
            "products:storefront_product_detail",
            pk=product_id,
        )

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:
        quantity = product.stock

    if product.stock == 0:
        return redirect(
            "products:storefront_product_detail",
            pk=product.pk,
        )

    cart = request.session.get("cart", {})

    product_id = str(product.pk)

    if product_id in cart:

        new_quantity = cart[product_id] + quantity

        cart[product_id] = min(
            new_quantity,
            product.stock,
        )

    else:

        cart[product_id] = quantity

    request.session["cart"] = cart

    request.session.modified = True

    return redirect("cart:cart_detail")


def cart_update(request, product_id):

    # Only allow POST requests
    if request.method != "POST":
        return redirect("cart:cart_detail")

    product = get_object_or_404(
        Product,
        pk=product_id,
    )

    # Get quantity submitted from cart
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    # Minimum quantity is 1
    if quantity < 1:
        quantity = 1

    # Maximum quantity is available stock
    if quantity > product.stock:
        quantity = product.stock

    # If product is out of stock,
    # remove it from the cart
    if product.stock == 0:

        cart = request.session.get("cart", {})

        cart.pop(str(product.pk), None)

        request.session["cart"] = cart
        request.session.modified = True

        return redirect("cart:cart_detail")

    # Get current cart
    cart = request.session.get("cart", {})

    product_id = str(product.pk)

    # Update only if product exists in cart
    if product_id in cart:

        cart[product_id] = quantity

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart:cart_detail")

def cart_remove(request, product_id):

    if request.method != "POST":
        return redirect("cart:cart_detail")

    cart = request.session.get("cart", {})

    cart.pop(str(product_id), None)

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart:cart_detail")