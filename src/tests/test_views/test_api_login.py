import pytest

from django.urls import reverse


@pytest.mark.django_db
class TestAPILogin:

    def test_api_login_view(self, api_client, user, token) -> None:

        response = api_client.post(reverse("api_login"),
                    {
                        "username": user.username,
                        "password": "password"
                    })
        
        assert response.status_code == 200
        
        response_token = response.data["token"]
        qs = token.objects.filter(key=response_token)
        
        assert qs.exists()
        assert response.data["username"] == user.username
        assert len(qs) == 1


    def test_api_logout_view(self, api_client, user, token) -> None:
        
        response = api_client.post(reverse("api_login"),
                    {
                        "username": user.username,
                        "password": "password"
                    })

        assert response.status_code == 200
        response_token = response.data["token"]
        
        response = api_client.post(reverse("api_logout"), {"token": response_token})

        assert response.status_code == 200
        assert response.data == {}
        assert token.objects.count() == 0


