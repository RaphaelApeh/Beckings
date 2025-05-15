from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .base import SerializerFactoryMixin

User = get_user_model()


class UserAPIView(SerializerFactoryMixin, ModelViewSet):

    queryset = User.objects.order_by("-date_joined")
    serializer_fields = ["username", "email"]
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


