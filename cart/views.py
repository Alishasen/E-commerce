import base64
import hashlib
import hmac
import json
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from products.models import Product, Order, OrderItem, Payment

from .forms import CheckoutForm


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

    # "Buy Now" reuses this same add-to-cart endpoint (no duplicate
    # logic) — it just adds the item as usual, then sends the user
    # straight to checkout with only this product pre-selected,
    # instead of back to the cart page.
    if request.POST.get("buy_now"):

        return redirect(
            f"{reverse('cart:checkout')}"
            f"?selected_products={product_id}"
        )

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


@login_required(login_url="accounts:login")
def checkout(request):

    cart = request.session.get("cart", {})

    # Cart is empty
    if not cart:
        return redirect("cart:cart_detail")

    # -------------------------
    # WHICH ITEMS ARE BEING CHECKED OUT
    # -------------------------
    # The cart page's checkboxes send the chosen product ids as
    # "selected_products" — as query params on the first GET (from
    # "Proceed to Checkout" or "Buy Now"), then carried through as
    # hidden fields on the checkout form's POST. If none were sent
    # at all (e.g. an old bookmark straight to /cart/checkout/),
    # fall back to the whole cart, same as before this feature.

    if request.method == "POST":
        raw_selected = request.POST.getlist("selected_products")
    else:
        raw_selected = request.GET.getlist("selected_products")

    if raw_selected:
        selected_ids = [
            product_id for product_id in raw_selected
            if product_id in cart
        ]
    else:
        selected_ids = list(cart.keys())

    # Nothing valid was selected (e.g. a stale/tampered selection)
    if not selected_ids:
        return redirect("cart:cart_detail")

    cart_items = []
    total = 0

    for product_id in selected_ids:

        quantity = cart[product_id]

        product = get_object_or_404(
            Product,
            pk=product_id,
        )

        # Check stock
        if product.stock < quantity:
            return redirect("cart:cart_detail")

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    # -------------------------
    # POST = CREATE ORDER
    # -------------------------

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            payment_method = data["payment_method"]

            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    total_amount=total,
                    full_name=data["full_name"],
                    email=data["email"],
                    phone=data["phone"],
                    shipping_address=data["shipping_address"],
                    shipping_city=data["shipping_city"],
                    shipping_notes=data["shipping_notes"],
                )

                for item in cart_items:

                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        quantity=item["quantity"],
                        price=item["product"].price,
                        subtotal=item["subtotal"],
                    )

                # -------------------------
                # CASH ON DELIVERY
                # -------------------------
                # No gateway to wait for, so the COD order is
                # finalized right away: stock is reserved and
                # the cart cleared. The payment itself stays
                # "pending" until cash is collected on delivery.

                if payment_method == "cod":

                    Payment.objects.create(
                        order=order,
                        payment_method="cod",
                        amount=total,
                        status="pending",
                        transaction_id=f"COD-{order.id}",
                    )

                    for item in cart_items:

                        product = item["product"]

                        # Re-check stock inside the transaction
                        # in case it changed since the cart page
                        # was loaded.
                        if product.stock < item["quantity"]:
                            transaction.set_rollback(True)
                            return redirect("cart:cart_detail")

                        product.stock -= item["quantity"]

                        product.save(
                            update_fields=["stock"]
                        )

                    # Remove only the items just ordered — any other
                    # products left in the cart (not selected for
                    # this checkout) stay there untouched.
                    for product_id in selected_ids:
                        cart.pop(product_id, None)

                    request.session["cart"] = cart
                    request.session.modified = True

                    return redirect(
                        "cart:payment_success",
                        order_id=order.id,
                    )

                # -------------------------
                # ESEWA
                # -------------------------
                # Stock, cart, and order status are only
                # finalized after eSewa verifies the payment
                # (see esewa_success). Go straight to eSewa —
                # no intermediate KHOJ payment-choice page.

                Payment.objects.create(
                    order=order,
                    payment_method="esewa",
                    amount=total,
                    status="pending",
                )

            return redirect(
                "cart:esewa_payment",
                order_id=order.id,
            )

    # -------------------------
    # GET = SHOW CHECKOUT
    # -------------------------

    else:

        form = CheckoutForm(
            initial={
                "full_name": (
                    request.user.get_full_name()
                    or request.user.username
                ),
                "email": request.user.email,
            }
        )

    return render(
        request,
        "cart/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
            "form": form,
            "selected_ids": selected_ids,
        },
    )


def generate_esewa_signature(
    total_amount,
    transaction_uuid,
    product_code,
):

    message = (
        f"total_amount={total_amount},"
        f"transaction_uuid={transaction_uuid},"
        f"product_code={product_code}"
    )

    secret_key = settings.ESEWA_SECRET_KEY.encode("utf-8")

    signature = hmac.new(
        secret_key,
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(signature).decode("utf-8")


@login_required(login_url="accounts:login")
def esewa_payment(request, order_id):
    
    print("Initiating eSewa payment for order ID:", order_id)
    print("request:", request)

    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )
    print("Initiating eSewa payment for order:", order.id)

    payment = get_object_or_404(
        Payment,
        order=order,
        payment_method="esewa",
    )
    
    print("Processing eSewa payment for order:", payment.order.id, "with payment ID:", payment.id)

    if payment.status == "success":
        return redirect(
            "cart:payment",
            order_id=order.id,
        )

    transaction_uuid = f"KHOJ-{order.id}-{order.created_at.strftime('%Y%m%d%H%M%S')}"

    total_amount = f"{payment.amount:.2f}"

    signature = generate_esewa_signature(
        total_amount=total_amount,
        transaction_uuid=transaction_uuid,
        product_code=settings.ESEWA_PRODUCT_CODE,
    )

    payment.transaction_id = transaction_uuid
    payment.save(
        update_fields=["transaction_id"]
    )

    context = {
        "payment_url": settings.ESEWA_PAYMENT_URL,
        "amount": total_amount,
        "tax_amount": "0",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": settings.ESEWA_PRODUCT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "signed_field_names": (
            "total_amount,"
            "transaction_uuid,"
            "product_code"
        ),
        "signature": signature,
        "success_url": request.build_absolute_uri(
            "/cart/payment/esewa/success/"
        ),
        "failure_url": request.build_absolute_uri(
            "/cart/payment/esewa/failure/"
        ),
    }

    return render(
        request,
        "cart/esewa_redirect.html",
        context,
    )


@login_required(login_url="accounts:login")
def esewa_success(request):

    encoded_data = request.GET.get("data")
    
    print("Received eSewa response data:", encoded_data)

    if not encoded_data:
        return render(
            request,
            "cart/payment_failed.html",
            {
                "message": "No payment response was received from eSewa."
            },
        )

    try:
        decoded_data = base64.b64decode(
            encoded_data
        ).decode("utf-8")
        
        print("Decoded eSewa response data:", decoded_data)

        response_data = json.loads(decoded_data)
        
    

    except (ValueError, json.JSONDecodeError):
        return render(
            request,
            "cart/payment_failed.html",
            {
                "message": "Invalid payment response."
            },
        )

    transaction_uuid = response_data.get(
        "transaction_uuid"
    )

    if not transaction_uuid:
        return render(
            request,
            "cart/payment_failed.html",
            {
                "message": "Transaction ID was not received."
            },
        )

    payment = get_object_or_404(
        Payment,
        transaction_id=transaction_uuid,
        order__user=request.user,
    )

    # Only process the payment if it is still pending
    if payment.status == "success":
        return redirect(
            "cart:payment_success",
            order_id=payment.order.id,
        )

    # Verify the transaction with eSewa
    verification_url = settings.ESEWA_STATUS_URL

    params = {
        "product_code": settings.ESEWA_PRODUCT_CODE,
        "total_amount": f"{payment.amount:.2f}",
        "transaction_uuid": transaction_uuid,
    }

    response = requests.get(
        verification_url,
        params=params,
        timeout=30,
    )

    if response.status_code != 200:
        return render(
            request,
            "cart/payment_failed.html",
            {
                "message": "Unable to verify payment with eSewa."
            },
        )

    verification_data = response.json()

    status = verification_data.get("status")

    if status != "COMPLETE":
        payment.status = "failed"
        payment.save(
            update_fields=["status"]
        )

        payment.order.status = "failed"
        payment.order.save(
            update_fields=["status"]
        )

        return render(
            request,
            "cart/payment_failed.html",
            {
                "message": (
                    "eSewa could not confirm this payment."
                )
            },
        )

    # Payment is verified by eSewa
    if status == "COMPLETE":

        with transaction.atomic():

            payment.status = "success"

            payment.esewa_ref_id = verification_data.get(
                "ref_id"
            )

            payment.save(
                update_fields=["status", "esewa_ref_id"]
            )

            order = payment.order

            # Prevent stock from being reduced twice
            if order.status != "paid":

                for item in order.items.select_related("product"):

                    product = item.product

                    # Check stock again before reducing it
                    if product.stock < item.quantity:

                        payment.status = "failed"
                        payment.save(
                            update_fields=["status"]
                        )

                        order.status = "failed"
                        order.save(
                            update_fields=["status"]
                        )

                        return render(
                            request,
                            "cart/payment_failed.html",
                            {
                                "message": (
                                    f"Not enough stock for "
                                    f"{product.name}."
                                )
                            },
                        )

                    product.stock -= item.quantity

                    product.save(
                        update_fields=["stock"]
                    )

                order.status = "paid"

                order.save(
                    update_fields=["status"]
                )

        # Remove only the items that were part of this order — any
        # other products the user had left in their cart (that
        # weren't part of this checkout) stay there untouched.
        cart = request.session.get("cart", {})

        for item in order.items.all():
            cart.pop(str(item.product_id), None)

        request.session["cart"] = cart
        request.session.modified = True

        return redirect(
            "cart:payment_success",
            order_id=order.id,
        )


@login_required(login_url="accounts:login")
def esewa_failure(request):
    
    print("eSewa payment failed. Request:", request)

    transaction_uuid = request.GET.get(
        "transaction_uuid"
    )

    if transaction_uuid:

        payment = Payment.objects.filter(
            transaction_id=transaction_uuid,
            order__user=request.user,
        ).first()

        if payment:
            payment.status = "failed"
            payment.save(
                update_fields=["status"]
            )

            payment.order.status = "failed"
            payment.order.save(
                update_fields=["status"]
            )

    return render(
        request,
        "cart/payment_failed.html",
        {
            "message": "Your eSewa payment was not completed."
        },
    )


@login_required(login_url="accounts:login")
def payment_success(request, order_id):

    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    payment = getattr(order, "payment", None)

    return render(
        request,
        "cart/payment_success.html",
        {
            "order": order,
            "payment": payment,
        },
    )


@login_required(login_url="accounts:login")
def order_detail(request, order_id):

    # get_object_or_404 with user=request.user means a user can
    # only ever open their own orders — anyone else's order_id
    # just 404s instead of leaking data.
    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    payment = getattr(order, "payment", None)

    items = order.items.select_related("product")

    return render(
        request,
        "cart/order_detail.html",
        {
            "order": order,
            "payment": payment,
            "items": items,
        },
    )