import copy
from typing import Any, TypeVar

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.exceptions import ValidationError

from products.models import Product
from helpers._typing import AuthUser
from helpers.serializers import serializer_factory
from helpers._cloudinary import use_cloudinary, CloudinaryImageField


UserType = TypeVar("UserType", AbstractBaseUser, AuthUser)
User = get_user_model()


class ProductListSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        UserSerializer = serializer_factory(User, fields=["username", "email"])
        self.fields["user"] = UserSerializer()
        if use_cloudinary():
            self.fields["image"] = CloudinaryImageField()

    updated_at = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "pk",
            "product_name",
            "product_slug",
            "product_description",
            "quantity",
            "updated_at",
            "timestamp",
            "price",
            "active",
        ]

    def get_updated_at(self, obj: Product) -> str:

        return obj.updated_at.strftime("%d/%m/%Y, %H:%M:%S")

    def get_timestamp(self, obj: Product) -> str:

        return obj.timestamp.strftime("%d/%m/%Y, %H:%M:%S")


class BaseProductSerializer(serializers.Serializer):
    """
    Base Product Serializer
    """

    def __init__(self, *args: list[Any], **kwargs: dict[str, Any]) -> None:

        super().__init__(*args, **kwargs)
        request = self.context["request"]
        self._user = request.user if hasattr(request, "user") else None
        if use_cloudinary() and hasattr(Product, "image"):
            self.fields["image"] = CloudinaryImageField(required=False)

    product_name = serializers.CharField()
    product_description = serializers.CharField()
    quantity = serializers.IntegerField(required=False)
    price = serializers.FloatField()
    active = serializers.BooleanField()

    def get_user(self) -> UserType:

        assert hasattr(self, "_user")
        assert self._user is not None

        user = self._user
        if not user.is_staff:
            raise ValidationError(f"{user.username} is not a staff user.")
        return user


class ProductCreateSerializer(BaseProductSerializer):

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Create Product"""
        user = self.get_user()
        product_name = attrs["product_name"]
        product = Product.objects.all()
        if product.filter(product_name__iexact=product_name).exists():
            raise ValidationError("product already exists.")

        obj = product.create(user=user, **attrs)
        attrs = copy.copy(attrs)
        attrs["product_slug"] = obj.product_slug
        attrs["user"] = model_to_dict(obj.user, fields=["username", "email"])

        return super().validate(attrs)


class ProductUpdateSerializer(BaseProductSerializer):

    def validate(self, data: dict[str, Any]):

        instance = self.instance
        assert instance is not None

        with transaction.atomic():
            for key, value in data.items():
                assert hasattr(instance, key), "%s has no attribute, %d" % (
                    instance.__class__.__name__,
                    key,
                )
                setattr(instance, key, value)
            instance.save()
        return data
