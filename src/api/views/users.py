from typing import TypeVar

from rest_framework import permissions, status, serializers
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .base import SerializerFactoryMixin
from helpers.serializers.users import ChangePasswordSerializer

User = get_user_model()

S = TypeVar("S", serializers.Serializer, serializers.ModelSerializer)


class ChangePasswordAPIView(GenericAPIView):

    serializer_class = ChangePasswordSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response({"success": "Password set Successfully."}, status=status.HTTP_200_OK)

class UserAPIView(SerializerFactoryMixin, ModelViewSet):

    queryset = User.objects.order_by("-date_joined")
    serializer_fields = ["pk", "username", "email", "last_login"]
    permission_classes = [
        permissions.IsAdminUser
    ]

    @action(["GET"],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request: Request) -> Response:

        obj = request.user
        serializer = self.get_serializer(obj, many=False)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


