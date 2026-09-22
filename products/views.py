from django.shortcuts import redirect, render,get_object_or_404
from .decorators import admin_required
from .forms import ProductForm, ReviewForm
from .models import Product, ProductImage, Banner, Category, Review, Order
from wishlist.models import Wishlist
from django.db.models import Avg, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Products at or below this stock level show up in the
# dashboard's "Low Stock Products" section.
LOW_STOCK_THRESHOLD = 5


@admin_required
def admin_dashboard(request):

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_customers = (
        User.objects
        .filter(groups__name="Customer")
        .distinct()
        .count()
    )

    # Revenue = orders that are actually paid/completed.
    # Pending (unconfirmed COD), failed, and cancelled orders
    # are excluded on purpose — they aren't real revenue yet.
    total_revenue = (
        Order.objects
        .filter(status__in=["paid", "completed"])
        .aggregate(total=Sum("total_amount"))
        ["total"] or 0
    )

    recent_orders = (
        Order.objects
        .select_related("user", "payment")
        .order_by("-created_at")[:5]
    )

    low_stock_products = (
        Product.objects
        .filter(stock__lte=LOW_STOCK_THRESHOLD)
        .order_by("stock")[:5]
    )

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "low_stock_products": low_stock_products,
    }

    return render(
        request,
        "products/admin_dashboard.html",
        context,
    )


@admin_required
def product_list(request):
    products = Product.objects.prefetch_related("images").all()

    context = {
        "products": products,
    }

    return render(
        request,
        "products/product_list.html",
        context,
    )

@admin_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save()

            images = request.FILES.getlist("images")

            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image,
                )

            return redirect("products:product_list")

    else:
        form = ProductForm()

    context = {
        "form": form,
    }

    return render(
        request,
        "products/product_form.html",
        context,
    )
    


@admin_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        pk=pk,
    )

    context = {
        "product": product,
    }

    return render(
        request,
        "products/product_detail.html",
        context,
    )
    
@admin_required   
def product_update(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        pk=pk,
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():
            form.save()

            images = request.FILES.getlist("images")

            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image,
                )

            return redirect(
                "products:product_detail",
                pk=product.pk,
            )

    else:
        form = ProductForm(instance=product)

    context = {
        "form": form,
        "product": product,
    }

    return render(
        request,
        "products/product_update.html",
        context,
    )
@admin_required
def product_image_delete(request, pk):
    image = get_object_or_404(
        ProductImage,
        pk=pk,
    )

    product_pk = image.product.pk

    if request.method != "POST":
        return redirect(
            "products:product_update",
            pk=product_pk,
        )

    image.delete()

    return redirect(
        "products:product_update",
        pk=product_pk,
    )
    
@admin_required    
def product_delete(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
    )

    if request.method == "POST":
        product.delete()

        return redirect(
            "products:product_list"
        )

    return redirect(
        "products:product_detail",
        pk=product.pk,
    )

def storefront_product_list(request):

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category")

    products = (
        Product.objects
       .prefetch_related("images")
       .annotate(
           average_rating=Avg("reviews__rating"),
           review_count=Count("reviews")
        )
    )

    trending_products = (
        Product.objects
        .filter(is_trending=True)
        .prefetch_related("images")
        .annotate(
            average_rating=Avg("reviews__rating"),
            review_count=Count("reviews")
        )
        .order_by("-created_at")
    )

    banners = Banner.objects.filter(
        is_active=True
    ).order_by("order")

    categories = Category.objects.all().order_by("name")


    # =========================
    # SEARCH
    # =========================

    if query:
        products = products.filter(
            name__icontains=query
        )


    # =========================
    # CATEGORY
    # =========================

    if category_id:
        products = products.filter(
            category_id=category_id
        )


    # =========================
    # WISHLIST
    # =========================

    wishlist_product_ids = set()

    if request.user.is_authenticated:

        wishlist_product_ids = set(
            Wishlist.objects.filter(
                user=request.user
            ).values_list(
                "product_id",
                flat=True
            )
        )


    return render(
        request,
        "products/storefront/product_list.html",
        {
            "products": products,
            "trending_products": trending_products,
            "categories": categories,
            "query": query,
            "banners": banners,
            "wishlist_product_ids": wishlist_product_ids,
        },
    )
    
def storefront_product_detail(request, pk):

    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        pk=pk,
    )

    is_in_wishlist = False

    if request.user.is_authenticated:

        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product,
        ).exists()

    reviews = Review.objects.filter(
        product=product
    ).select_related("user")

    review_count = reviews.count()

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    review_form = ReviewForm()

    context = {
        "product": product,
        "is_in_wishlist": is_in_wishlist,
        "reviews": reviews,
        "review_count": review_count,
        "average_rating": average_rating,
        "review_form": review_form,
    }

    return render(
        request,
        "products/storefront/product_detail.html",
        context,
    )
@login_required(login_url="accounts:login")
def add_review(request, pk):

    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

    return redirect(
        "products:storefront_product_detail",
        pk=product.pk,
    )