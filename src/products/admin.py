from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    list_display = ["user__username", "product_name", "product_slug", "active"]
    search_fields = ["user__username", "products_name", "product_description"]
    prepopulated_fields = {"product_slug": ("product_name",)}
    fieldsets = (
        (None, {"fields": ("product_name",)}),
        ("Price", {"fields": ("price",)}),
        ("Description", {"fields": ("product_description",)}),
        ("Extra Data", {"fields": ("active", "product_slug")})
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return True if request.user.is_superuser else False
    
    def has_delete_permission(self, request: HttpRequest, obj: "Product" | None = ...):
        return super().has_delete_permission(request, obj)

    def save_model(self, request: HttpRequest, obj: "Product", form, change) -> Any:
        obj.user = request.user
        return super().save_model(request, obj, form, change)