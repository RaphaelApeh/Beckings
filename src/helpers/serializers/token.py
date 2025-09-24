from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.exceptions import AuthenticationFailed

from api.models import get_token_model


Token = get_token_model()


class PasswordField(CharField):

    def __init__(self, **kwargs):
        style = kwargs.setdefault("style", {})
        style["input_type"] = "password"
        kwargs["write_only"] = True
        super().__init__(**kwargs)


class TokenLoginSerializer(serializers.Serializer):

    username = CharField()
    password = PasswordField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)
        request = self.context["request"]
        username = data.pop("username", None)
        password = data.pop("password", None)
        credentials = {"username": username, "password": password}
        user = authenticate(request=request, **credentials)
        if user is None:
            raise AuthenticationFailed("invaild credentials :(.")
        update_last_login(sender=None, user=user)
        obj, _ = Token.objects.get_or_create(user=user)
        data["token"] = obj.key
        data["username"] = username
        return data

    def __class_getitem__(cls, *args: list[Any], **kwargs: dict[str, Any]):

        return cls


class TokenLogoutSerializer(serializers.Serializer):

    token = serializers.CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[None, None]:

        token = attrs["token"]
        try:
            obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            raise serializers.ValidationError("invalid token %s" % token)
        else:
            obj.delete()

        return {}
