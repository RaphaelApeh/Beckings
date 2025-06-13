from __future__ import annotations

import enum
from typing import Optional, Any, \
                    TypeVar, NoReturn
from dataclasses import dataclass

from django.db.models import F
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Product, Order
from helpers._typing import Bit


U = TypeVar("U")


class OrderStatusOptions(enum.Enum):

    DELIVERED = "delivered"
    PENDING = "pending"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class AddOrder:

    product_instance: Product
    request: Optional[Any] = None
    view: Optional[Any] = None


    def __post_init__(self) -> None:

        assert self.product_instance is not None
        assert isinstance(self.product_instance, Product)


    def validate(self, number_of_items: int) -> NoReturn:
        errors = []
        match number_of_items:
            case 0:
                errors.append("Can not add an empty order.")
            case n if n < 1:
                errors.append("Can't add nagative item")
            case s if s > self.product_instance.quantity:
                errors.append("Not enough quantity to order.")
            case _:
                pass
        if errors:
            raise ValidationError(" ".join(errors))


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

