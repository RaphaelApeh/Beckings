from typing import Any

from django.contrib.admin import action
from django.template.response import TemplateResponse

from helpers.enum import OrderStatusOptions
from .forms import (
    ExportForm
)


class ReadOnlyMixin:

    exclude_fields = None

    def has_add_permission(self, request, obj=None) -> bool:
        return False
    
    def get_form(self, request, obj=None, change=None, **kwargs: Any):
        
        form = super().get_form(request, obj, change, **kwargs)
        for field in form.base_fields:
            if field not in self.exclude_fields:
                form.base_fields[field].disabled = True
        return form


@action(description="Export Filters")
def export_quertyset_filter(model_admin, request, queryset):
    
    assert hasattr(model_admin, "resource_classes")

    context = model_admin.admin_site.each_context(request)

    form = ExportForm()

    context.update(
        {
            "opts": model_admin.opts,
            "form": form,
            "object_list": queryset
        }
    )
    request.current_app = model_admin.admin_site.name
    return TemplateResponse(
        request,
        "admin/filter_export_data.html",
        context
    )


@action(description="User Order Delivered")
def user_order_delivered_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusOptions.DELIVERED.value)
    model_admin.message_user(request, "Updated user order")
    
@action(description="User Order Pending")
def user_order_pending_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusOptions.PENDING.value)
    model_admin.message_user(request, "Updated user order")

@action(description="User Order Cancelled")
def user_order_cancelled_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusOptions.CANCELLED.value)
    model_admin.message_user(request, "Updated user order")
    