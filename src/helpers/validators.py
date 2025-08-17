from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):

    message = _(
        "Enter a valid phone number" 
        "e.g (+2348033758395)."
        )
    
    regex = r"^(?:\+234|0)[789][01]\d{8}$"
    flags = 0
