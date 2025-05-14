from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from products.models import Product
from .base import SerializerFactoryMixin


class ProductViewSet(SerializerFactoryMixin, ModelViewSet):

    queryset = Product.objects.select_related("user").order_by("-pk")
    serializer_fields = ["pk", "product_name", "product_description", "price", "active"]
    permission_classes = [permissions.IsAdminUser]


