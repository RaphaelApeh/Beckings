from django.db.models import Model
from rest_framework.serializers import ModelSerializer

from .users import UserSerializer


__all__ = [
    "UserSerializer",
    "serializer_factory",
]


def serializer_factory(model: type[Model], serializer = ModelSerializer, *, fields: list[str] | str | None = None, exclude: list[str] | None =None) -> ModelSerializer:

    assert model is not None
    assert issubclass(model, Model)

    meta_data = {
        "model": model,
        "fields": fields if fields is not None else "__all__"
    }
    if exclude:
        meta_data["exclude"] = exclude
    Meta = type("Meta", (), meta_data)

    class_name = model.__name__ + "Serializer" if not model.__name__.endswith("Serializer") else model.__name__
    serializer_data = {
        "Meta": Meta
    }
    return type(class_name, (serializer,), serializer_data)

