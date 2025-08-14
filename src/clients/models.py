import re

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


PHONE_NUMBER_REGEX = r"^(?:\+234|0)[789][01]\d{8}$"
NIGERIA_PHONE_NUMBER = re.compile(
    PHONE_NUMBER_REGEX
)


class Client(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    address = models.TextField(blank=True, default="")
    phone_number = models.CharField(
        blank=True,
        null=True,
        validators=(
            RegexValidator(PHONE_NUMBER_REGEX, _("Enter a Valid Phone Number")),
        ),
        unique=True
        )

    def __str__(self):
        return self.user.username


@receiver(models.signals.post_save, sender=get_user_model())
def create_user_client(signal, sender, instance, **kwargs):
    created = kwargs.get("created", False)
    if instance and created:
        if Client.objects.filter(user=instance).exists():
            return
        Client._default_manager.create(user=instance)
