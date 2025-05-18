from typing import Any, TypeVar

from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import APIException

from helpers._typing import AuthUser
from .token import PasswordField


UserType = TypeVar("UserType", AbstractUser, AuthUser)


class _APIException(APIException):

    status_code = 404
    default_detail = "error"


class ChangePasswordSerializer(serializers.Serializer):

    old_password = PasswordField()
    
    new_password = PasswordField()
    
    confirmation_password = PasswordField()


    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)

        old_password = data.pop("old_password", None)

        new_password = data.pop("new_password", None)
        confirmation_password = data.pop("confirmation_password")

        if new_password != confirmation_password:
            raise _APIException("Password not match.")
        try:
            validate_password(new_password)
        
        except ValidationError as e:
            raise _APIException(" ".join(e.messages))
        
        user: UserType = self.context["request"].user

        if not user.check_password(old_password):
            raise _APIException("incorrect password.", )
        
        user.set_password(new_password)
        user.save()
        return {}
    