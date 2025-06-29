import random

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
    settings.DEFAULT_FROM_EMAIL = "team@beckings.com"
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


@pytest.fixture
def products(db):
    """
    Products
    """
    from products.models import Product

    return Product.objects.all()

@pytest.fixture
def product(db):

    from products.models import Product
    return Product

@pytest.fixture(autouse=True)
def user(db):
    """
    Create dumb user credencials 
    """
    return User.objects.create_superuser(username="test_user", email="admin@test.com", password="password")


@pytest.fixture(autouse=True)
def token(db):
    from api.models import get_token_model
    Token = get_token_model()
    return Token


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture for an authenticated API client
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def products_factory(db):
    from helpers.factories import ProductFactory
    
    return ProductFactory.create_batch(random.randint(1, 10))