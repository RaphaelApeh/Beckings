from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs) -> None:
        kwargs["widget"] = forms.PasswordInput()
        super().__init__(*args, **kwargs)


class LoginForm(forms.Form):

    login = forms.CharField(label="Username or Email", required=True)

    password = PasswordField()

    def __init__(self, *args,  **kwargs) -> None:
        super().__init__(args, **kwargs)
        request = kwargs.pop("request", None)
        assert request is not None
        self._request = request


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = ""

    
    def clean(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            self.add_error("email", "Email already exists.")
        return super().clean()
    
    