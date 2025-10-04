from django.urls import reverse
from rest_framework import status
from django.utils.lorem_ipsum import words

from django.contrib.auth import get_user_model


User = get_user_model()


def test_create_api_view_with_admin(authenticated_client, products) -> None:
    data = {
        "product_name": "APITEST",
        "product_description": "Hello World",
        "price": 343.2,
        "active": True,
    }
    response = authenticated_client.post(reverse("product_list"), data)

    assert response.status_code == 201
    assert len(products) > 0  # Insert to the product model
    assert response.data["product_name"] == data["product_name"]


def test_create_api_view_not_admin(db, api_client, products) -> None:

    user = User.objects.create_user("testuser1234", password="password")
    api_client.force_authenticate(user=user)
    data = {
        "product_name": "APITEST",
        "product_description": "Hello World",
        "price": 343.2,
        "active": True,
    }
    response = api_client.post(reverse("product_list"), data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(products) == 0


def test_product_retrieve_api_view(authenticated_client, products) -> None:
    obj = products.create(product_name="Hello WORLD", product_description=words(12))
    response = authenticated_client.get(
        reverse(
            "product_retrieve", kwargs={"pk": obj.pk, "product_slug": obj.product_slug}
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["product_name"] == obj.product_name


def test_product_update_api_view(authenticated_client, products) -> None:

    obj = products.create(product_name="Hello WORLD", product_description=words(12))

    data = {"product_description": "A good product description."}
    response = authenticated_client.put(
        reverse(
            "product_retrieve", kwargs={"pk": obj.pk, "product_slug": obj.product_slug}
        ),
        data,
    )

    assert response.data["product_description"] == data["product_description"]
    assert response.status_code == status.HTTP_200_OK


def test_product_delete_api_view(authenticated_client, products) -> None:

    obj = products.create(product_name="Hello WORLD", product_description=words(12))

    response = authenticated_client.delete(
        reverse(
            "product_retrieve", kwargs={"pk": obj.pk, "product_slug": obj.product_slug}
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not products.filter(product_name=obj.product_name).exists()
