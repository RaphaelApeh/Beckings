from collections import OrderedDict
from typing import Any, Union, Generator, TypeVar

from django.forms.fields import Field, ChoiceField
from django.core.exceptions import ValidationError

from import_export.formats.base_formats import Format


__all__ = ["FormatChoiceField"]

T = TypeVar("T")


class FormatChoiceField(ChoiceField):
    """Form field for django-import-export Format class"""

    def __init__(self, formats=(), encoding=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.encoding = encoding
        self.formats = formats

    def _get_fromats(self) -> Union[Any, None, OrderedDict[str, Any]]:
        return self._formats

    def _set_formats(self, formats) -> None:

        self.choices = self._formats_choices(formats, self.encoding)

        if formats is not None:
            self._formats = self._build_formats(
                formats, encoding=self.encoding, as_dict=True
            )
            return
        self._formats = {}

    formats = property(_get_fromats, _set_formats)

    @staticmethod
    def _formats_choices(formats, encoding=None) -> Union[None, tuple[str, str]]:

        if formats is None:
            return
        return (
            (str(f(encoding).get_title()), f(encoding).get_title().upper())
            for f in formats
        )

    @staticmethod
    def _build_formats(
        formats, *, encoding=None, raise_asserts=True, as_dict=False
    ) -> Generator[tuple[str, Any], None, None] | OrderedDict[str, Any]:

        assert formats is not None or not raise_asserts
        assert (
            hasattr(formats, "__iter__") or not raise_asserts
        ), "formats need to be an Iterable but"
        "Got {}".format(type(formats).__name__)
        assert (
            all((f for f in formats if issubclass(f, Format))) or not raise_asserts
        ), "formats needs to be a subclass of Format class."

        choices = (
            (str(f(encoding).get_title()), f(encoding=encoding)) for f in formats
        )
        if not as_dict:
            return choices
        return OrderedDict(choices)

    def to_python(self, value) -> T:
        if value in self.empty_values:
            return None
        format = self.formats.get(value)
        if format is not None:
            return format
        raise ValidationError(self.error_messages["invalid"])

    def validate(self, value):
        Field.validate(self, value)
