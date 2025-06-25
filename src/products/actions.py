from typing import Any

from django.contrib.admin import action

from helpers.enum import OrderStatusOptions


class ReadOnlyMixin(object):

    def has_change_permission(self, request: Any, obj: Any | None = None) -> bool:
        return False

    def has_add_permission(self, request, obj=None) -> bool:
        return False


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
    