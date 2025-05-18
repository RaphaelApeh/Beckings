from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token


class PasswordField(CharField):


    def __init__(self, **kwargs):
        style = kwargs.setdefault("style", {})
        style["input_type"] = "password"
        kwargs["write_only"] = True
        super().__init__(**kwargs)


class TokenLoginSerializer(serializers.Serializer):

    login = CharField()
    password = PasswordField()


    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)
        request = self.context["request"]
        login = data.pop("login", None)
        password = data.pop("password", None)
        credentials = {
            "request": request,
            "username": login,
            "password": password
        }
        user = authenticate(**credentials)
        if user is None:
            raise AuthenticationFailed("invaild credentials :(.")
        update_last_login(sender=None, user=user)    
        obj, _ = Token.objects.get_or_create(user=user)
        data["token"] = obj.key
        data["username"] = login
        return data
    

    def __class_getitem__(cls, *args: list[Any], **kwargs: dict[str, Any]):

        return cls