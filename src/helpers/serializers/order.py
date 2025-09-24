from __future__ import annotations

from typing import Any, NoReturn

from rest_framework import serializers

from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, AbstractUser
from django.utils.translation import gettext_lazy as _

from products.order_utils import AddOrder
from products.models import OrderProxy, Product
from products.models import OrderStatusChoices
from helpers.serializers import serializer_factory

from .products import ProductListSerializer


User = get_user_model()


class UserOrderSerializer(serializers.ModelSerializer):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        UserSerializer = serializer_factory(User, fields=["username", "email"])
        self.fields["user"] = UserSerializer()

    product = ProductListSerializer()

    class Meta:
        model = OrderProxy
        fields = ("product", "user", "manifest", "status", "number_of_items")


class UserOrderCreateSerializer(serializers.Serializer):

    default_error_messages = {
        "required": _("{field} is required."),
    }

    status = serializers.ChoiceField(
        choices=OrderStatusChoices.choices, default="pending"
    )

    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:

        super().__init__(*args, **kwargs)
        self.fields["manifest"] = serializers.CharField()
        self.fields["number_of_items"] = serializers.IntegerField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:

        user = self.user
        data = {}
        product = self.model

        if product is None:
            self.fail("required", field="Product")

        if not user:
            self.fail("required", field="User")

        kwargs = {}

        if (number_of_items := attrs.get("number_of_items")) is not None:
            kwargs["number_of_items"] = number_of_items
            data["number_of_items"] = number_of_items

        if manifest := attrs.get("manifest"):
            kwargs["manifest"] = manifest
            data["manifest"] = manifest

        if status := data.get("status"):
            kwargs["status"] = status
            data["status"] = status

        self.validate_item(product, data.get("number_of_items"))
        self.save_order(product, data)
        qs = user.order_set.all()

        kwargs["message"] = _("Added Item")
        kwargs["item_count"] = qs.count()

        kwargs["total_sum"] = qs.aggregate(total_sum=Sum("product__price"))["total_sum"]

        kwargs["user"] = {"username": user.username, "email": user.email}
        return self.returned_data(**kwargs)

    @property
    def user(self) -> AbstractUser:
        if not getattr(self, "_user", None):
            self._user = self.context["request"].user

        assert self._user is not None
        assert not isinstance(self._user, AnonymousUser)

        return self._user

    def validate_item(self, product: Product, number_of_items: int) -> NoReturn:

        errors = []
        assert number_of_items is not None

        match number_of_items:
            case 0:
                errors.append("Can not add an empty order.")
            case n if n < 1:
                errors.append("Can't add nagative item")
            case s if s > product.quantity:
                errors.append("Not enough quantity to order.")
            case _:
                pass
        if errors:
            raise serializers.ValidationError(" ".join(errors))

    @property
    def model(self):

        if not getattr(self, "_model", None):
            try:
                model = self.context["model"]
            except KeyError:
                raise KeyError("The context dict has not key 'model' ")
            self._model = model
            assert isinstance(self._model, Product)
        return self._model

    def save_order(self, product: Product, data: dict[str, Any]) -> None:

        user = self.user

        AddOrder(product_instance=product).create(user, data)

    def returned_data(self, **kwargs: dict[Any, Any]) -> dict[Any, Any]:
        # TODO
        return kwargs
