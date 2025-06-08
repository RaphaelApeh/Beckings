from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class PasswordField(forms.CharField):

    widget = forms.PasswordInput


class LoginForm(forms.Form):

    login = forms.CharField(label="Username or Email", required=True, widget=forms.TextInput({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"}))

    password = PasswordField(widget=forms.PasswordInput({"class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5"}))

    def __init__(self, *args, **kwargs) -> None:
        request = kwargs.pop("request", None)
        self._user = None
        self.init_request(request)
        
        super().__init__(*args, **kwargs)
        
        if not hasattr(self, "request"):
            raise AttributeError(f"{self.__class__.__name__} has not attribute request.")

    
    def init_request(self, request) -> None:

        if request is not None:
            self.request = request
        
        return None
    
    def get_user(self):
        
        return self._user

    def clean(self):
        login = self.cleaned_data.get("login")
        password = self.cleaned_data.get("password")
        user = authenticate(self.request, username=login, password=password)
        if user is None:
            self.add_error(None, "Invaild credentials :(")
        self._user = user
        return super().clean()


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
    
