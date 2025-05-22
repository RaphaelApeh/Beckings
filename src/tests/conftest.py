import pytest

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    """
    Rest Framework API Client
    """
    return APIClient()


@pytest.fixture(autouse=True)
def console_email_backend(settings) -> None:
    """
    For sending emails to the console.
    """
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"



@pytest.fixture(autouse=True)
def user(db):
    """
    Create dumb user credencials 
    """
    return User.objects.create_user(username="test_user", password="password")


