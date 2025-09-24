from contextlib import contextmanager
import pytest
from django.urls import reverse
from products.models import Product
from helpers.factories import ProductFactory


@contextmanager
def create_products(size=1):
    ProductFactory.create_batch(size)
    yield


@pytest.mark.django_db
@create_products()
def test_product_update(client, user):
    obj = Product.objects.get()
    client.force_login(user)
    response = client.put(
        obj.get_absolute_url(),
        data={"product_description": "Hello World"},
        HTMX_REQURST=True,
    )
    obj.refresh_from_db()

    assert response.status_code == 200
    assert obj.product_description == "Hello World"


@pytest.mark.django_db
def test_product_delete(client, user):
    obj = Product.objects.create(user=user, product_name="Test Product")
    client.force_login(user)
    response = client.delete(
        reverse("product_delete", args=(obj.pk, obj.product_slug)), HTMX_REQURST=True
    )
    obj.refresh_from_db()

    assert response.status_code == 200
    assert Product.objects.count() == 0
