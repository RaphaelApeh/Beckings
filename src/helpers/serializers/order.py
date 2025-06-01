from typing import Any

from rest_framework import serializers
from django.contrib.auth import get_user_model

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
            "manifest"
        )
