from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from products.models import Product
from helpers.decorators import paginate
from helpers.filters import ModelSearchFilterBackend
from helpers.serializers.order import UserOrderCreateSerializer
from helpers.serializers.products import (
    ProductListSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
)


@paginate(PageNumberPagination, page_size=10)
class ProductListCreateView(GenericAPIView):

    serializer_class = ProductListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Product.objects.select_related("user")
    filter_backends = (ModelSearchFilterBackend,)

    def get_serializer_class(self):

        match self.request.method:
            case "POST":
                return ProductCreateSerializer
            case _:

                assert self.serializer_class

                return self.serializer_class

    def get_permissions(self) -> list:

        match self.request.method:
            case "POST":
                self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query",
                type=OpenApiParameter.QUERY,
                required=False,
                description="Search for Products.",
            )
        ],
        responses=ProductListSerializer(many=True),
    )
    def get(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class ProductRetrieveView(GenericAPIView):

    queryset = Product.objects.select_related("user")
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Product:

        model = self.get_queryset().model
        kwargs = self.kwargs
        obj = get_object_or_404(
            model, id=kwargs["pk"], product_slug=kwargs["product_slug"]
        )

        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ProductUpdateSerializer
        if self.request.method == "POST":
            return UserOrderCreateSerializer
        return super().get_serializer_class()

    def get(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:

        serializer = self.get_serializer(self.get_object(), many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):

        kwargs = {"request": self.request, "format": self.format_kwarg, "view": self}
        if self.request.method == "POST":
            kwargs["model"] = self.get_object()

        return kwargs

    def post(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        """
        Create user orders
        """
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        serializer = self.get_serializer(
            instance=self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args: list[str], **kwargs: dict[str, Any]) -> Response:
        return self.put(request, *args, **kwargs)
