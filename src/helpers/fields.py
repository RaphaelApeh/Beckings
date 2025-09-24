"""Helpers for models"""

from django.db import models
from django.core.checks import Error
from django.utils.text import slugify
from django.core.exceptions import FieldDoesNotExist


class AutoSlugField(models.SlugField):

    def __init__(self, perform_from=None, *args, **kwargs):
        self.perform_from = perform_from
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_perform_from(),
            *self._check_perform_from_obj(),
        ]

    def _check_perform_from(self):
        errors = []
        if not (hasattr(self, "perform_from") and self.perform_from):
            msg = ""
            errors.append(Error(msg))
        return errors

    def _check_perform_field_exists(self):
        errors = []
        try:
            self.model._meta.get_field(self.perform_from)
        except FieldDoesNotExist:
            errors.append(
                Error(f"{self.model.__name__} has no field {self.perform_from!r}")
            )
        return errors

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.perform_from:
            kwargs["perform_from"] = self.perform_from
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if add:
            perform_from = getattr(model_instance, self.perform_from)
            value = slugify(perform_from)
            setattr(model_instance, self.attname, value)
        return value
