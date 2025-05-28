import pytest

from django.urls import reverse

@pytest.mark.django_db
class TestUserAPIView:


    def test_change_password_view(self, authenticated_client) -> None:
        
        data = {
            "old_password": "password",
            "new_password": "password1",
            "confirmation_password": "password1"
        }
        response = authenticated_client.post(reverse("api_user_change_password"), data)

        assert response.status_code == 200
        assert response.data["success"] == "Password set Successfully."