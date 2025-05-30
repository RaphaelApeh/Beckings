import pytest

from django.urls import reverse

@pytest.mark.django_db
class TestUserAPIView:


    def test_change_password_view(self, authenticated_client, user) -> None:
        
        data = {
            "old_password": "password",
            "new_password": "sjsoddjso", # valid password
            "confirmation_password": "sjsoddjso"
        }
        response = authenticated_client.post(reverse("api_user_change_password"), data)

        assert response.status_code == 200
        assert response.data["success"] == "Password set Successfully."
        assert user.check_password(data["new_password"])


    def test_invalid_change_password_view(self, authenticated_client, user) -> None:
        
        data = {
            "old_password": "password",
            "new_password": "password1", # invalid password
            "confirmation_password": "password1"
        }
        response = authenticated_client.post(reverse("api_user_change_password"), data)

        assert response.status_code == 404
        assert "This password is too common." == response.data["detail"]


