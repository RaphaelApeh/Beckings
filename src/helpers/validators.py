from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class PhoneNumberValidator(RegexValidator):

    message = _("Enter a valid phone number" "e.g (+2348033758395).")

    regex = r"^(?:\+234|0)[789][01]\d{8}$"
    flags = 0


def validate_phone_number(phone_number):
    from clients.models import Client

    PhoneNumberValidator()(phone_number)

    if Client.objects.filter(phone_number__iexact=phone_number).exists():
        raise ValidationError("Phone Number already exists.")
