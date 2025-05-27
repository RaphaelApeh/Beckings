import pytest

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestTokenLogin:

    def test_token_valid_login_view(self, api_client):
        data = {
            "username": "test_user",
            "password": "password"
        }
        response = api_client.post(reverse("api_login"), data)
        assert response.status_code == status.HTTP_200_OK


    def test_token_invalid_login_view(self, api_client):
        data = {
            "username": "not a valid username",
            "password": "password"
        }
        response = api_client.post(reverse("api_login"), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == "invaild credentials :(."
    
    
    def test_invalid_data(self, api_client) -> None:

        data = {
            "username": "test_user"
        }
        response = api_client.post(reverse("api_login"), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        error = response.data["password"]
        assert "This field is required." in error
