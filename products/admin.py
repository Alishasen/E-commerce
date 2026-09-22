from django.contrib import admin

from .models import Product, ProductImage, Banner,Category, Order, OrderItem, Payment


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ("name",)
    search_fields = ("name",)
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "stock",
        "discount",
        "is_trending",
        "created_at",
    )
    list_filter = ("is_trending",)
    search_fields = ("name", "description")
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "image",
        "created_at",
    )
    
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    ordering = (
        "order",
    )
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "full_name",
        "phone",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "full_name",
        "email",
        "phone",
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "quantity",
        "price",
        "subtotal",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "payment_method",
        "amount",
        "status",
        "transaction_id",
        "esewa_ref_id",
        "created_at",
    )

    list_filter = (
        "payment_method",
        "status",
    )

    search_fields = (
        "transaction_id",
        "esewa_ref_id",
        "order__id",
    )