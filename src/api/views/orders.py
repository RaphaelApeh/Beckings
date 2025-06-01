from typing import Any

from django.db.models import QuerySet

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

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

