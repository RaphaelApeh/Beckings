from __future__ import annotations

import binascii
import os

from django.db import models
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured


def get_token_model() -> type[Token]:

    token = getattr(settings, "API_TOKEN_MODEL", None)

    try:
        model = apps.get_model(token, require_ready=False)

    except Exception as err:

        raise ImproperlyConfigured('"API_TOKEN_MODEL" was not set properly.') from err

    else:
        return model


def create_token_expire(sender, instance, *args, **kwargs) -> None:

    expire_when = settings.API_TOKEN_EXPIRE_TIME

    if instance.expired_at is None:
        created = instance.created

        expire = created + expire_when

        instance.expired_at = expire
        instance.save()

    return None


class Token(models.Model):

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    expired_at = models.DateTimeField(_("Expired"), blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["key"], name="token_key_idx")]
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

    def is_expired(self) -> bool:

        if self.expired_at is None:
            return False
        return timezone.now() >= self.expired_at


models.signals.post_save.connect(create_token_expire, sender=Token)
