from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404

from .forms import ProductForm
from .models import Product, ProductImage


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
    products = Product.objects.prefetch_related("images").all()

    context = {
        "products": products,
    }

    return render(
        request,
        "products/storefront/product_list.html",
        context,
    )
    
def storefront_product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related("images"),
        pk=pk,
    )

    context = {
        "product": product,
    }

    return render(
        request,
        "products/storefront/product_detail.html",
        context,
    )