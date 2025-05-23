from typing import Any, TypeVar

from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.exceptions import ValidationError

from products.models import Product
from helpers._typing import AuthUser


UserType = TypeVar("UserType", AbstractBaseUser, AuthUser)


class  ProductListSerializer(serializers.ModelSerializer):


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


    updated_at = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            "pk",
            "product_name",
            "product_slug",
            "product_description",
            "updated_at",
            "timestamp",
            "price",
            "active"
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

    product_name = serializers.CharField()
    product_description = serializers.CharField()
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
        """ Create Product """
        user = self.get_user()
        
        Product.objects.create(user=user, **attrs)

        return super().validate(attrs)


class ProductUpdateSerializer(BaseProductSerializer):


    def validate(self, data: dict[str, Any]):
        
        instance = self.instance
        assert instance is not None

        with transaction.atomic():
            for (key, value) in data.items():
                assert hasattr(instance, key), "%s has no attribute, %d" % (instance.__class__.__name__, key)
                setattr(instance, key, value)
            instance.save()
        return data
    

