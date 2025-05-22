import pytest
from pytest_django import asserts as astx

from django.urls import reverse


@pytest.mark.django_db
class TestLoginView:
    

    def test_valid_login(self, client) -> None:
        data = {
            "login": "test_user",
            "password": "password"
        }
        
        response = client.post(reverse("login"), data)

        assert response.status_code == 302

        astx.assertRedirects(response, reverse("products"))


    def test_invalid_login(self, client) -> None:

        data = {}
        data["login"] = "invaliduser"
        response = client.post(reverse("login"), data)

        assert "This field is required." in response.text


