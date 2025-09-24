from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _

from .decorators import classproperty


class EnumChoiceMixin:

    @classproperty
    def choices(cls) -> list[str]:
        return [x.value for x in cls]


class OrderStatusChoices(TextChoices):

    delivered = "delivered", _("Delivered")
    pending = "pending", _("Pending")
    cancelled = "cancelled", _("Cancelled")
    in_transit = "in_transit", _("In Transit")
