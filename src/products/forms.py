from __future__ import annotations

from typing import Any

from django import forms
from django.core.exceptions import ImproperlyConfigured


from clients.models import PHONE_NUMBER_REGEX
from .models import Product, Order, ORDER_CHOICES
from .order_utils import AddOrder
from helpers.enum import ExportType



BORDER = (
    "w-full",
    "border",
    "border-gray-200",
    "shadow-xs",
)

FORM_TEXT = (
    "text-black",
    "rounded-md",
)

TEXT = (
    "font-medium",
    "text-gray-900"
)

PADDING = (
    "p-2",
    "mb-2",
    "mt-2"
)

FOCUS = (
    "focus:z-10",
    "focus:ring-4",
    "focus:ring-gray-200",
    "focus:outline-none"
)

SELECT = (
    *BORDER,
    *PADDING,
    "md:w-auto",
    "flex",
    "items-center",
    "hover:bg-gray-100",
    "rounded-lg",
    "bg-white",
    *FOCUS,
    *TEXT

)

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
    

class AddOrderForm(forms.ModelForm):
    
    product = forms.ModelChoiceField(
        Product.objects.filter(active=True),
        widget=forms.HiddenInput
    )
    address = forms.CharField(
        widget=forms.Textarea
    )
    phone_number = forms.RegexField(
        regex=PHONE_NUMBER_REGEX,
        widget=forms.TelInput({
            "pattern": PHONE_NUMBER_REGEX
        })
    )
    number_of_items = forms.IntegerField(
        label="Quantity",
        widget=forms.NumberInput(
            attrs={
                "min": 0
            }
        )
    )

    class Meta:
        model = Order
        fields = ("number_of_items", )
    
    field_order = (
        "address",
        "phone_number",
        "number_of_items"
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        request = kwargs.pop("request", None)
        view = kwargs.pop("view", None)

        assert request is not None and \
                view is not None

        super().__init__(*args, **kwargs)
        self._init_fields()
        self.request = request
        self.view = view

    def _init_fields(self):
        client = self.user.client
        for name in self.fields:
            if not getattr(client, name, None):
                continue
            value = getattr(client, name, None)
            if value is not None:
                self.fields.pop(name)

    @property
    def user(self):
        if not hasattr(self, "_user"):
            self._user = self.request.user
        return self._user

    def clean(self) -> dict:

        data = self.cleaned_data

        product_instance = data["product"]
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
    

    def _save_client_data(self, user, data):

        from django.core.exceptions import FieldDoesNotExist

        client = user.client
        opts = client._meta
        for name in self.fields:
            if name not in opts.concrete_fields:
                continue
            try:
                field = opts.get_field(name)
                field.save_form_data(client, data[name])
            except (ValueError, FieldDoesNotExist):
                continue
        
        client.save()


    def save(self, commit=True) -> Any:
       instance = super().save(commit=False) #noqa
       cleaned_data = self.cleaned_data
       # Do not call instance.save()
       self._save_client_data(self.user, cleaned_data)
       return AddOrder(
           product_instance=cleaned_data["product"]
       ).create(self.user, cleaned_data) # This will save the order and return the order


class ProductImportForm(forms.Form):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        css_class = {*BORDER, *PADDING, *FORM_TEXT, "focus:ring-gray-800"}
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = " ".join(list(css_class))

    file = forms.FileField()
    format = forms.ChoiceField(choices=ExportType.choices)


class ExportForm(forms.Form):

    format = forms.ChoiceField(choices=ExportType.choices,
                               widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs) -> None:
        
        queryset = kwargs.pop("queryset", None)
        resource = kwargs.pop("resource", None)

        super().__init__(*args, **kwargs)
        self.resource = resource
        self.queryset = queryset
    
    def _export_type(self, export, format):

        return {
            "json": export.json,
            "csv": export.csv,
            "yaml": export.yaml,
            "html": export.html
        }.get(format, "json")
    
    def export(self, queryset=None, **kwargs):

        self.full_clean()
        
        if queryset is None:
            queryset = self.queryset

        if (resource := self.resource) is not None:
            format = self.cleaned_data["format"]
        
            if hasattr(resource, "export_data"):
                ds = resource.export_data(queryset, **kwargs)
        
                return self._export_type(ds, format)
        
            kw = {**kwargs, **(self.resource_kwargs() or {})}
            ds = resource(**kw).export(queryset)
        
            return self._export_type(ds, format)

        raise ImproperlyConfigured("Can't use `export` method when resource is None")

    def resource_kwargs(self, **kwargs):
        return kwargs
    

class OrderActionForm(forms.Form):

    action = forms.ChoiceField(
        choices={"": "------", **ORDER_CHOICES},
        widget=forms.Select
        )


class CommentForm(forms.Form):

    message = forms.CharField(
        label="Your Comment",
        widget=forms.Textarea
    )
    product_id = forms.IntegerField(
        widget=forms.HiddenInput
    )


class ReplyForm(forms.Form):

    message = forms.CharField(
        label="Message"
    )
    comment_id = forms.IntegerField(
        widget=forms.HiddenInput
    )
    redirect_url = forms.CharField(
        widget=forms.HiddenInput
    )

class SearchForm(forms.Form):

    search = forms.CharField(
        widget=forms.SearchInput # 5.2
    )

