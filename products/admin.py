from django.contrib import admin

from .models import Product, ProductImage, Banner,Category


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