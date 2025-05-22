import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
class TestLogoutView:

    def test_logout_view_with_get(self, client):

        client.login(username="test_user", password="password")
        response = client.get(reverse("logout"))
        
        assert response.status_code == 200
        assert "Logout" in response.text

    def test_logout_view_with_post(self, client):
        
        client.login(username="test_user", password="password")
        response = client.post(reverse("logout"))

        assert response.status_code == 302
        assertRedirects(response, reverse("login"))