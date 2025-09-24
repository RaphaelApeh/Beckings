from typing import Any

from django.db.models import QuerySet

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.mixins import DestroyModelMixin

from products.models import Order
from api.permissions import IsUser
from helpers.serializers.order import UserOrderSerializer


class BaseGenericAPIView(GenericAPIView):

    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.select_related("user", "product")

    def get_queryset(self) -> QuerySet:

        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class UserOrderListAPIView(BaseGenericAPIView):

    serializer_class = UserOrderSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("timestamp", "status", "order_id")

    def get(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:

        queryset = self.filter_queryset(self.get_queryset())
        serailizer = self.get_serializer(queryset, many=True)

        return Response(serailizer.data, status=status.HTTP_200_OK)


class UserOrderRetrieveAPIView(DestroyModelMixin, BaseGenericAPIView):

    serializer_class = UserOrderSerializer
    permission_classes = (IsAuthenticated, IsUser)

    def get_object(self):

        kwargs = {"order_id": self.kwargs["order_id"]}
        model = self.get_queryset().model
        try:
            obj = model.objects.get(**kwargs)
        except model.DoesNotExist:
            raise NotFound("object does not exists.")

        self.check_object_permissions(self.request, obj)
        self.object = obj
        return obj

    def get(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:

        instance = self.object if hasattr(self, "object") else self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:

        return self.destroy(request, *args, **kwargs)
