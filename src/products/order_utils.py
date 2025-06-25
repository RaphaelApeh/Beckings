from __future__ import annotations

from typing import Optional, Any, \
                    TypeVar
from dataclasses import dataclass

from django.db.models import F
from django.db import transaction

from .models import Product, Order
from helpers._typing import Bit
from helpers.enum import OrderStatusOptions


U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class AddOrder:

    product_instance: Product
    request: Optional[Any] = None
    view: Optional[Any] = None


    def __post_init__(self) -> None:

        assert self.product_instance is not None
        assert isinstance(self.product_instance, Product)


    def create(self, user: U, data: Bit, **kwargs: Any) -> AddOrder:
        
        product_instace = self.product_instance
        number_of_items = data.get("number_of_items")
        manifest = data.get("manifest", "")
        assert product_instace is not None and number_of_items is \
                not None

        with transaction.atomic():
            product_instace.quantity = F("quantity") - number_of_items
            product_instace.save()
            order = Order.objects.create(
                                product=product_instace,
                                user=user,        
                                number_of_items=number_of_items,
                                manifest=manifest)
            order.status = OrderStatusOptions.PENDING.value
            order.save()
        return self

