from typing import Any, List

from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin
)
from import_export.admin import (
    ImportExportMixin,
    ExportMixin,
    ExportActionMixin,
    )
from guardian.admin import GuardedModelAdminMixin
from unfold.admin import ModelAdmin, GenericStackedInline

from helpers import resources
from .actions import (
    ReadOnlyMixin,
    user_order_delivered_action,
    user_order_cancelled_action,
    user_order_pending_action
)
from .models import (
    Product,
    OrderProxy,
    Comment,
    Reply
)


User = get_user_model()

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):

    list_display = (*BaseUserAdmin.list_display, "is_active")


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):...


class CommentInline(GenericStackedInline):

    model = Comment
    extra = 1


@admin.register(Comment)
class CommentAdmin(ModelAdmin):

    list_display = (
        "user__username",
        "message",
        "timestamp"
    )
    list_filter = (
        "user",
    )

@admin.register(Reply)
class ReplyAdmin(ModelAdmin):

    list_display = (
        "user__username",
        "message"
    )

@admin.register(Product)
class ProductAdmin(
                GuardedModelAdminMixin,
                ImportExportMixin,
                ExportActionMixin, 
                ModelAdmin
                ):
    
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
    list_filter = (
        "price",
        "active",
    )
    resource_classes = (resources.ProductResource, )
    inlines = (
        CommentInline,
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")
    
    def has_add_permission(self, request) -> bool:
        return True if request.user.is_superuser else False
    
    def has_delete_permission(self, request: HttpRequest, obj: Product | None = None):
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj: Product, form, change) -> Any:
        obj.user = request.user
        return super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        if hasattr(obj, "image"):
            obj.image.delete()
        return super().delete_model(request, obj)


@admin.register(OrderProxy)
class OrderAdmin(ReadOnlyMixin, ExportMixin, ModelAdmin):

    fields: List[str] = ["user", "product", "manifest", "status"]
    readonly_fields: List[str] = ["timestamp"]
    list_display: tuple[str] = (
                    "user__username", 
                    "product__product_name",
                    "status",
                    "timestamp")
    search_fields = (
        "status",
        "user__username",
        "product__product_name"
    )
    actions = (
        user_order_delivered_action,
        user_order_pending_action,
        user_order_cancelled_action
    )
    exclude_fields = ("status",)
    resource_classes = (resources.OrderResource,)

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).select_related("user", "product").\
        order_by("-timestamp")


