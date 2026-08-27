from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductTag,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "sort_order",
        "name",
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

    fields = (
        "image",
        "alt_text",
        "is_primary",
        "sort_order",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "product_type",
        "price",
        "currency",
        "stock",
        "is_active",
        "is_featured",
        "total_sales",
    )

    list_filter = (
        "product_type",
        "category",
        "is_active",
        "is_featured",
        "is_new",
        "currency",
    )

    search_fields = (
        "name",
        "description",
        "short_description",
        "brand",
        "sku",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    autocomplete_fields = (
        "category",
    )

    filter_horizontal = (
        "tags",
    )

    inlines = [
        ProductImageInline,
    ]

    readonly_fields = (
        "total_sales",
        "views",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "short_description",
                    "description",
                    "brand",
                    "tags",
                )
            },
        ),
        (
            "Product Type",
            {
                "fields": (
                    "product_type",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "compare_at_price",
                    "currency",
                )
            },
        ),
        (
            "Inventory",
            {
                "fields": (
                    "sku",
                    "stock",
                    "unlimited_stock",
                )
            },
        ),
        (
            "Store Visibility",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                    "is_new",
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "rating",
                    "total_sales",
                    "views",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "is_primary",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "is_primary",
    )

    search_fields = (
        "product__name",
        "alt_text",
    )


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }
