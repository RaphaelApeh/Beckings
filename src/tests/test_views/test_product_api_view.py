import pytest

from django.urls import reverse
from rest_framework import status

from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestProductAPIViews:

    def test_create_api_view_with_admin(self, authenticated_client, products) -> None:
        data = {
            "product_name": "APITEST",
            "product_description": "Hello World",
            "price": 343.2,
            "active": True
        }
        response = authenticated_client.post(reverse("product_list"), data)
        
        assert response.status_code == 201
        assert len(products) > 0 # Insert to the product model


    def test_create_api_view_not_admin(self, db, api_client) -> None:
        
        user = User.objects.create_user("testuser1234", password="password")
        api_client.force_authenticate(user=user)
        data = {
            "product_name": "APITEST",
            "product_description": "Hello World",
            "price": 343.2,
            "active": True
        }
        response = api_client.post(reverse("product_list"), data)

        assert response.status_code == status.HTTP_403_FORBIDDEN



