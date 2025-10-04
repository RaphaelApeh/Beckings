from django import forms
from django.contrib.auth import get_user_model

from helpers.forms.mixins import TailwindRenderFormMixin
from .models import FeedBack


UserModel = get_user_model()


class FeedBackForm(TailwindRenderFormMixin, forms.ModelForm):

    non_user_fields = ("user",)

    email = forms.EmailField(
        label="Your Email"
    )
    user = forms.ModelChoiceField(
        UserModel._default_manager.filter(is_active=True),
        widget=forms.HiddenInput,
        required=False
    )
    user_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput
    )

    class Meta:
        model = FeedBack
        fields = (
            "email",
            "user_id",
            "complain",
            "complain_type"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        non_user_fields = self.non_user_fields
        user_ = (
            self.data.get("user") or self.initial.get("user")
        )
        if not user_ and non_user_fields:
            for name in non_user_fields:
                del self.fields[name]
        elif user_:
            del self.fields["email"]
    
    def clean(self):
        user = self.initial.get("user")
        cleaned_data = super().clean()
        if not user:
            return cleaned_data
        cleaned_data.setdefault("user", user)
        return cleaned_data

    def _post_clean(self):
        cleaned_data = self.cleaned_data.copy()
        while "user" in cleaned_data:
            user = cleaned_data["user"]
            cleaned_data["email"] = user.email
            cleaned_data["user_id"] = user.pk
            del cleaned_data["user"]
        self.cleaned_data = cleaned_data
        super()._post_clean()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance.get_user(), instance