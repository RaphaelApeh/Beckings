import re

from django.db import models
from django.conf import settings
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
