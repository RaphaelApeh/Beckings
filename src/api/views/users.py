from typing import TypeVar, Any

from rest_framework import permissions, status, serializers
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .base import SerializerFactoryMixin
from ..permissions import IsUser
from helpers.serializers.users import ChangePasswordSerializer, \
                                    UserCreationSerializer, \
                                    UserUpdateSerializer


User = get_user_model()

S = TypeVar("S", serializers.Serializer, serializers.ModelSerializer)


class ChangePasswordAPIView(GenericAPIView):

    serializer_class = ChangePasswordSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:

        serializer = self.get_serializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)

        return Response({"success": "Password set Successfully."}, status=status.HTTP_200_OK)


class UserAPIView(SerializerFactoryMixin, ModelViewSet):

    queryset = User.objects.order_by("-date_joined")
    serializer_fields: tuple[str, ...] = ("pk",
                        "username", 
                        "email",
                        "first_name",
                        "last_name", 
                        "last_login")
    permission_classes = (
        IsUser,
    )

    def get_permissions(self):
        
        if self.action == "create":
            return [permissions.AllowAny()]
        
        if self.action == "list":
            return [permissions.IsAdminUser()]
    
        return super().get_permissions()


    def get_serializer_class[T](self) -> type[T]:

        if self.action == "create":
            return UserCreationSerializer
        
        if self.action == "update":
            return UserUpdateSerializer
        return super().get_serializer_class()


    def perform_update(self, serializer) -> None:
        
        return None #
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
        

    def create(self, request, *args: Any, **kwargs: Any) -> Response:
        
        serializer = self.get_serializer(data=request.data)
        self.update
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data, 
                        status=status.HTTP_201_CREATED)


    @action(["GET"],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request: Request) -> Response:

        obj = request.user
        serializer = self.get_serializer(obj, many=False)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


