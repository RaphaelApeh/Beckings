from enum import Enum

from .decorators import classproperty


class EnumChoiceMixin:

    @classproperty
    def choices(cls) -> list[str]:
        return [x.value for x in cls]


class ExportType(EnumChoiceMixin, Enum):
    JSON = "json", "Json"
    CSV = "csv", "Csv"
    YAML = "yaml", "Yaml"


class OrderStatusOptions(Enum):

    DELIVERED = "delivered"
    PENDING = "pending"
    CANCELLED = "cancelled"