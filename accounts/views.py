from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, render

from products.models import Order

from .forms import RegisterForm


def register_view(request):

    if request.user.is_authenticated:
        return redirect(
            "products:storefront_product_list"
        )

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            customer_group = Group.objects.get(
               name="Customer"
            )

            user.groups.add(customer_group)

            login(request, user)

            return redirect(
               "products:storefront_product_list"
            )

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


def login_view(request):

    if request.user.is_authenticated:

        if (
            request.user.is_superuser
            or request.user.groups.filter(name="Admin").exists()
        ):
            return redirect(
                "products:admin_dashboard"
            )

        return redirect(
            "products:storefront_product_list"
        )

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            if (
                user.is_superuser
                or user.groups.filter(name="Admin").exists()
            ):
                return redirect(
                    "products:admin_dashboard"
                )

            return redirect(
                "products:storefront_product_list"
            )

        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password.",
            },
        )

    return render(
        request,
        "accounts/login.html",
    )


def logout_view(request):

    logout(request)

    return redirect(
        "products:storefront_product_list"
    )


@login_required(login_url="accounts:login")
def account_view(request):

    # filter(user=request.user) means this can only ever show
    # the logged-in user's own orders — nobody else's.
    orders = (
        Order.objects
        .filter(user=request.user)
        .select_related("payment")
        .order_by("-created_at")
    )

    return render(
        request,
        "accounts/account.html",
        {
            "orders": orders,
        },
    )