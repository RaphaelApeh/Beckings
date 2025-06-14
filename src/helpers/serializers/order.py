from typing import Any

from rest_framework import serializers

from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _

from products.order_utils import AddOrder
from products.models import OrderProxy, Product
from helpers.serializers import serializer_factory

from .products import ProductListSerializer


User = get_user_model()


class UserOrderSerializer(serializers.ModelSerializer):


    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        UserSerializer = serializer_factory(User,
                                            fields=["username", "email"])
        self.fields["user"] = UserSerializer()


    product = ProductListSerializer()

    class Meta:
        model = OrderProxy
        fields = (
            "product",
            "user",
            "manifest",
            "number_of_items"
        )


class UserOrderCreateSerializer(serializers.Serializer):

    default_error_messages = {
        'required': _('{field} is required.'),
    }

    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:
        
        super().__init__(*args, **kwargs)
        self.product_id = self.context["product_id"]
        self.fields["manifest"] = serializers.CharField()
        self.fields["number_of_items"] = serializers.IntegerField()


    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        
        product_id = self.product_id if hasattr(self, "product_id") else \
                            None
        
        user = self.context["request"].user
        data = {}

        assert user is not None
        assert not isinstance(user, AnonymousUser)
        
        if product_id is None:
            self.fail("required", field="Product Id")
        user = self.context["request"].user
        
        if not user:
            self.fail("required", field="User")
        
        kwargs = {
            "user": user,
            "product_id": int(product_id)
        }
        
        try:
            product = Product.objects.get()
        except Product.DoesNotExist:
            raise serializers.ValidationError("product does not exists.")
        
        if (number_of_items := attrs.get("number_of_items")) is not None:
            kwargs["number_of_items"] = number_of_items
            data["number_of_items"] = number_of_items
        if manifest := attrs.get("manifest"):
            kwargs["manifest"] = manifest
            data["manifest"] = manifest

        AddOrder(
            product_instance=product
        ).create(user, data)

        kwargs.pop("user")
        qs = user.order_set.all()
        kwargs["message"] = _("Added Item")
        kwargs["item_count"] = qs.count()
        kwargs["total_sum"] = qs.aggregate(total_sum=Sum("product__price"))["total_sum"]
        kwargs["user"] = {
            "username": user.username,
            "email": user.email
        }
        return kwargs



