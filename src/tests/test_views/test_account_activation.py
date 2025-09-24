import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
def test_account_activation_off(client, settings):
    data = {
        "username": "john",
        "phone_number": "09063847274",
        "email": "johndoe@test.com",
        "password1": "btgrfecced",
        "password2": "btgrfecced",
    }
    settings.USE_ACCOUNT_ACTIVATION_VIEW = False

    response = client.post(reverse("register"), data)
    assert response.status_code == 302
    assertRedirects(response, reverse("login"))


@pytest.mark.django_db
def test_account_activation_on(client, settings):
    data = {
        "username": "john",
        "phone_number": "09063847274",
        "email": "johndoe@test.com",
        "password1": "btgrfecced",
        "password2": "btgrfecced",
    }
    settings.USE_ACCOUNT_ACTIVATION_VIEW = True

    response = client.post(reverse("register"), data)
    assert response.status_code == 200
