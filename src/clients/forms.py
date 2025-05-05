from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class PasswordField(forms.CharField):

    widget = forms.PasswordInput


class LoginForm(forms.Form):

    login = forms.CharField(label="Username or Email", required=True, widget=forms.TextInput({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"}))

    password = PasswordField(widget=forms.PasswordInput({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"}))


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = ""
            self.fields[field].widget.attrs.update({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"})

    
    def clean(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            self.add_error("email", "Email already exists.")
        return super().clean()
    
    