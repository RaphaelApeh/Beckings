from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from products.models import Product
from helpers.serializers.products import (
    ProductListSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer
)



class ProductListCreateView(GenericAPIView):


    serializer_class = ProductListSerializer
    queryset = Product.objects.select_related("user")


    def get_serializer_class(self):

        if self.request.method == "POST":
            return ProductCreateSerializer
        return self.serializer_class


    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                type=OpenApiParameter.QUERY,
                required=False,
                description="Search for Products."
            )
        ],
        responses=ProductListSerializer(many=True)
    )
    def get(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class ProductRetrieveView(GenericAPIView):

    queryset = Product.objects.select_related("user")
    serializer_class = ProductListSerializer

    def get_object(self):

        model = self.get_queryset().model 
        kwargs = self.kwargs
        obj = get_object_or_404(model, id=kwargs["pk"], product_slug=kwargs["product_slug"])
    
        self.check_object_permissions(self.request, obj)

        return obj
    
    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProductUpdateSerializer
        return super().get_serializer_class()


    def get(self, request, *args:  list[str], **kwargs: dict[str, Any]) -> Response:

        serializer = self.get_serializer(self.get_object(), many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    def put(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def patch(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        return self.put(request, *args, **kwargs)

