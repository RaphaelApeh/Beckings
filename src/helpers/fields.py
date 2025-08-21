from collections import OrderedDict

from django.forms.widgets import Select
from django.forms.fields import Field, ChoiceField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from import_export.formats.base_formats import Format



class FormatChoiceField(ChoiceField):

    widget = Select
    default_error_messages = {
        "invalid_choice": _(
            "Select a valid choice. %(value)s is not one of the available choices."
        ),
    }

    def __init__(self, formats=(), encoding=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.encoding = encoding
        self.formats = formats

    def _get_fromats(self):
        return self._formats
    
    def _set_formats(self, formats) -> None:

        self.choices = (
            self._build_formats_choice(
                formats,
                encoding=self.encoding,
                raise_asserts=False
            )
        )
        formats = (
            (str(i), f(encoding=self.encoding))
            for (i, f) in enumerate(formats)
        )
        self._formats = formats

    formats = property(_get_fromats, _set_formats)


    @staticmethod
    def _build_formats_choice(formats, *, encoding=None, raise_asserts=True, as_dict=False):

        assert formats is not None or not raise_asserts
        assert hasattr(formats, "__iter__") or not raise_asserts, \
        "formats need to be an Iterable but"
        "Got {}".format(formats.__name__)
        assert all((f for f in formats if issubclass(f, Format))) or not raise_asserts, \
        "formats needs to be a subclass of Format class."

        choices = (
            (str(i), f(encoding=encoding)).get_title()
            for (i, f) in enumerate(formats)
        )
        if not as_dict:
            return choices
        return OrderedDict(choices)
    
    def prepare_value(self, value):
        if isinstance(value, Format):
            return value.get_title()
        return super().prepare_value(value)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        if isinstance(value, type) and issubclass(value, Format):
            value = value(encoding=self.encoding)
            assert value in self.formats, \
            "Invalid format"
            return value
        if isinstance(value, Format):
            assert value in self.formats, "Invalid format"
            return value
        try:
            value = int(value)
            format = self.formats[value]
            return format
        except (ValueError, TypeError, IndexError):
            raise ValidationError(
                self.default_error_messages["invalid_choice"],
                params={"value": str(value)}
            )
    
    def validate(self, value):
        Field.validate(self, value)

