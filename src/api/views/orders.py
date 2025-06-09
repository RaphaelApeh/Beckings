from typing import Any, Union

from django.db.models import QuerySet

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from products.models import OrderProxy
from helpers.serializers.order import UserOrderSerializer


class BaseGenericAPIView(GenericAPIView):

    permission_classes = (
        IsAuthenticated,
    )
    
    def get_queryset(self) -> QuerySet:

        qs = self.request.user.order_set.select_related("user", "product")
        return qs


class UserOrderListAPIView(BaseGenericAPIView):

    serializer_class = UserOrderSerializer


    def get(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        
        queryset = self.filter_queryset(self.get_queryset())
        serailizer = self.get_serializer(queryset, many=True)
        
        return Response(serailizer.data, status=status.HTTP_200_OK)



class UserOrderRetrieveAPIView(BaseGenericAPIView):


    serializer_class = UserOrderSerializer

    def get_object(self) -> Union[OrderProxy, Response]:

        kwargs = {
            "order_id": self.kwargs["order_id"]
        }
        try:
            obj = OrderProxy.objects.get(**kwargs)
        except OrderProxy.DoesNotExist:
            return Response("object does not exists.", status=status.HTTP_404_NOT_FOUND)
        else:
            self.object = obj
            return obj


    def get(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        serializer = self.get_serializer(self.get_object())

        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, *args: list[Any], **kwargs: dict[str, Any]) -> Response:
        ...

