from typing import Any

from rest_framework import serializers
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from products.models import OrderProxy
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
        self.fields["manifest"] = serializers.CharField(allow_blank=True)
        self.fields["number_of_items"] = serializers.IntegerField(required=False)


    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        
        product_id = self.product_id if hasattr(self, "product_id") else \
                            None
        if product_id is None:
            self.fail("required", field="Product Id")
        user = self.context["request"].user
        if not user:
            self.fail("required", field="User")
        manifest = attrs.get("manifest", "")
        kwargs = {
            "user": user,
            "product_id": int(product_id)
        }
        if manifest:
            kwargs["manifest"] = manifest
        OrderProxy.objects.create(**kwargs)

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



