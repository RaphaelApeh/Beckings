from typing import Any

from django.contrib.admin import action

from helpers.enum import OrderStatusChoices


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


@action(description="%(verbose_name)s Delivered")
def user_order_delivered_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusChoices.delivered.value)
    model_admin.message_user(request, "Updated user order")
    

@action(description="%(verbose_name)s Pending")
def user_order_pending_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusChoices.pending.value)
    model_admin.message_user(request, "Updated user order")


@action(description="%(verbose_name)s Cancelled")
def user_order_cancelled_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusChoices.cancelled.value)
    model_admin.message_user(request, "Updated user order")


@action(description="%(verbose_name)s Trans-it")
def user_order_in_transit_action(model_admin, request, queryset) -> None:
    
    queryset.update(status=OrderStatusChoices.in_transit.value)
    model_admin.message_user(request, "Updated user order")