from datetime import datetime
from typing import Any, List

from django.contrib import admin
from django.http import HttpRequest, \
                        HttpResponse
from django.db.models import QuerySet
from import_export.admin import (
    ImportExportModelAdmin,
    ExportMixin
    )

from helpers import resources
from .actions import (
    ReadOnlyMixin,
    export_quertyset_filter,
    user_order_delivered_action,
    user_order_cancelled_action,
    user_order_pending_action
)
from .models import (
    Product,
    OrderProxy
)
from .forms import (
    ExportForm
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
    actions = (
        export_quertyset_filter,
    )
    resource_classes = (resources.ProductResource, )

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
    
    def export_queryset(self, request, queryset):
        resource = self.resource_classes[0]
        form = ExportForm(request.POST, resource=resource, queryset=queryset)
        data = form.export()
        format = form.cleaned_data["format"]
        time_str = datetime.now().strftime("%d/%m/%Y")
        response = HttpResponse(data)
        response["Content-Disposition"] = 'attachment; filename="product_{}.{}"'.format(time_str, format)
        return response



@admin.register(OrderProxy)
class OrderAdmin(ReadOnlyMixin, ExportMixin, admin.ModelAdmin):

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
    exclude_fields = ("status",)
    resource_classes = (resources.OrderResource,)

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).select_related("user", "product").\
        order_by("-timestamp")


