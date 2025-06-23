from typing import Any, List

from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from import_export.admin import ImportExportModelAdmin

from helpers import resources
from .actions import (
    ReadOnlyMixin,
    user_order_delivered_action,
    user_order_cancelled_action,
    user_order_pending_action
)
from .models import (
    Product,
    OrderProxy
)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    
    list_display = ["user__username", "product_name", "product_slug", "active"]
    search_fields = ["user__username", "product_name", "product_description"]
    prepopulated_fields = {"product_slug": ("product_name",)}
    fieldsets = (
        (None, {"fields": ("product_name",)}),
        ("Price", {"fields": ("price",)}),
        ("Description", {"fields": ("product_description",)}),
        ("Extra Data", {"fields": ("active", "product_slug")}),
        ("Quantity", {"fields": (
            "quantity",
        )})
    )
    resource_classes = (resources.ProductResource, )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")
    
    def has_add_permission(self, request: HttpRequest) -> bool:
        return True if request.user.is_superuser else False
    
    def has_delete_permission(self, request: HttpRequest, obj: Product | None = ...):
        return super().has_delete_permission(request, obj)

    def save_model(self, request: HttpRequest, obj: Product, form, change) -> Any:
        obj.user = request.user
        return super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        if hasattr(obj, "image"):
            obj.image.delete()
        return super().delete_model(request, obj)



@admin.register(OrderProxy)
class OrderAdmin(ReadOnlyMixin, admin.ModelAdmin):

    fields: List[str] = ["user", "product", "manifest", "status"]
    readonly_fields: List[str] = ["timestamp"]
    list_display: tuple[str, ...] = (
                    "user__username", 
                    "product__product_name",
                    "status",
                    "timestamp")
    actions = (
        user_order_delivered_action,
        user_order_pending_action,
        user_order_cancelled_action
    )

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).select_related("user", "product").\
        order_by("-timestamp")

