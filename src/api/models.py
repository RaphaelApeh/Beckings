from __future__ import annotations

import binascii
import os

from django.db import models
from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured



def get_token_model() -> type[Token]:

    
    token = getattr(settings, "API_TOKEN_MODEL", None)

    try:
        model = apps.get_model(token, require_ready=False)

    except Exception as err:

        raise ImproperlyConfigured("\"API_TOKEN_MODEL\" was not set properly.") from err
    
    else:
        return model



class Token(models.Model):

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    expired = models.DateTimeField(_("Expired"), blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["key"], name="token_key_idx")
        ]
        swappable = "API_TOKEN_MODEL"

    def save(self, *args, **kwargs) -> None:
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls) -> str:
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self) -> str:
        return self.key

