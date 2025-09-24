from typing import Type, TypeVar, Generic

from rest_framework.serializers import ModelSerializer

from helpers._typing import List
from helpers.serializers import serializer_factory


T = TypeVar("T")


class SerializerFactoryMixin(Generic[T]):

    serializer_fields: List | None = None
    exclude_fields: List | None = None

    def get_serializer_class(self) -> Type[ModelSerializer]:

        if self.serializer_class is not None:
            return self.serializer_class

        serializer_fields = getattr(self, "serializer_fields", None)
        model = getattr(self, "model", None) or self.get_queryset().model

        return serializer_factory(
            model, fields=serializer_fields, exclude=getattr(self, "exclude_fields", [])
        )
