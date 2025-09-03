from __future__ import annotations

from typing import Any

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from import_export.formats import base_formats

from .models import Product, Order
from helpers.enum import OrderStatusChoices
from helpers.forms import FormatChoiceField
from .order_utils import AddOrder


ORDER_CHOICES = OrderStatusChoices.choices

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
        fields = ("number_of_items", "manifest")
        labels = {
            "manifest": _("Note (Optional)")
        }
    
    field_order = (
        "address",
        "phone_number",
        "number_of_items"
    )

    def __init__(self, *args: Any, request=None, **kwargs: Any) -> None:

        view = kwargs.pop("view", None)

        assert request is not None and \
                view is not None

        super().__init__(*args, **kwargs)
        self.request = request
        self.view = view
        self._init_fields()

    def _init_fields(self):
        client = self.user.client
        for name in self.fields.copy():
            if not getattr(client, name, None):
                continue
            value = getattr(client, name)
            if value:
                self.fields.pop(name)

    @property
    def user(self):
        if not hasattr(self, "_user"):
            self._user = self.request.user
        return self._user

    def clean(self) -> dict:

        data = self.cleaned_data

        product_instance = data.get("product")
        number_of_items = data.get("number_of_items", 0)

        if product_instance is None:
            raise self.add_error(None, "product can't be None")
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


class ExportForm(forms.Form):

    format = FormatChoiceField(formats=base_formats.DEFAULT_FORMATS)

    def __init__(self, *args, **kwargs) -> None:
    
        super().__init__(*args, **kwargs)
        
        format = self.fields["format"]
        
        if len(format.choices):
            format.choices = (("", "-------"), *format.choices)

    def date_format(self, format, object_name: str)-> str:
        date_str = timezone.now().strftime("%d-%m-%Y")
        return "{}-{}.{}".format(
            date_str, 
            object_name.lower(), 
            format.get_extension()
        )


class OrderActionForm(forms.Form):

    action = forms.ChoiceField(
        choices=ORDER_CHOICES,
        widget=forms.Select
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        action = self.fields["action"]
        if isinstance(action.choices, (list, tuple)):
            action.choices = ("", "----") + action.choices


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

