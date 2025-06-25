from __future__ import annotations

from enum import Enum
from typing import Any

from django import forms
from django.forms.utils import pretty_name

from .models import Product
from .order_utils import AddOrder
from helpers.decorators import classproperty


class ExportType(Enum):
    JSON = "json", "Json"
    CSV = "csv", "Csv"
    YAML = "yaml", "Yaml"

    @classproperty
    def choices(cls) -> list[str, tuple[str, ...]]:
        return [x.value for x in cls]

class TextField(forms.CharField):
    
    widget = forms.Textarea


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product 
        fields = [
            "product_name",
            "product_description",
            "price",
            "quantity",
            "active"
        ]
    
    def __init__(self, *args, **kwargs) -> None:
        request = kwargs.pop("request", None)
        assert request is not None
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields["active"].widget.attrs["class"] = "None"

    @property
    def user(self):

        if not getattr(self, "_user", None):
            self._user = self.request.user
        assert self._user is not None
        return self._user

    @user.setter
    def user(self, value) -> None:
        self._user = value
    
    def clean(self):
        data = super().clean()
       
        return data

    def save(self, commit=True) -> Product:
        instance = super().save(commit=False)
        if instance.user is None:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    

class AddOrderForm(forms.Form):


    def __init__(self, *args: Any, **kwargs: Any) -> None:

        request = kwargs.pop("request", None)
        view = kwargs.pop("view", None)

        assert request is not None and \
                view is not None

        super().__init__(*args, **kwargs)
        
        self.request = request
        self.view = view

        for field in self.fields:
            self.fields[field].widget.attrs.setdefault("placeholder", pretty_name(field))
        self.fields["number_of_items"].widget.attrs.update({"min": 0})        


    manifest = TextField(required=False)
    number_of_items = forms.IntegerField()

    def clean(self):

        data = self.cleaned_data
        
        product_instance = self.product
        number_of_items = data.get("number_of_items", 0)

        match number_of_items:
            case 0:
                self.add_error(None, "Can not add an empty order.")
            case n if n < 1:
                self.add_error(None, "Can't add nagative item")
            case s if s > product_instance.quantity:
                self.add_error(None, "Not enough quantity to order.")
            case _:
                pass
        return data
    
    @property
    def product(self):
        if not hasattr(self, "_product"):
            self._product = getattr(self.view, "product")
        return self._product
    

    def save(self, user, **kwargs: Any) -> None:
       data = self.cleaned_data
       
       AddOrder(
           product_instance=self.product
       ).create(user, data)



class ProductImportForm(forms.Form):

    file = forms.FileField()
    format = forms.ChoiceField(choices=ExportType.choices)


class ExportTypeForm(forms.Form):

    format = forms.ChoiceField(choices=ExportType.choices)
