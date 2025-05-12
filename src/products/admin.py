from typing import Any

from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    list_display = ["user__username", "product_name", "product_slug", "active"]
    prepopulated_fields = {"product_slug": ("product_name",)}
    fieldsets = (
        (None, {"fields": ("product_name",)}),
        ("Price", {"fields": ("price",)}),
        ("Description", {"fields": ("product_description",)}),
        ("Extra Data", {"fields": ("active", "product_slug")})
    )

    def save_model(self, request, obj, form, change) -> Any:
        obj.user = request.user
        return super().save_model(request, obj, form, change)