import json
from pathlib import Path

import pytest

from django.urls import reverse
from django.core.files import File


@pytest.mark.django_db
def test_product_export(client, products_factory, user):

    products_factory
    client.force_login(user)
    response = client.get(reverse("export_import_product"), {"format": "json"})

    assert response.status_code == 200

    assert isinstance(json.loads(response.content), list)


def test_product_import(client, user, product):
    
    with open(Path().resolve() / "data.json") as json_file:
        file = File(json_file)
    client.force_login(user)
    response = client.post(reverse("export_import_product"),
                           data={
                               "file": file,
                               "format": "json"
                           },
                           content_type="multipart/form-data", 
                           follow=True)
    
    assert "Data Saved." in response.text
    assert product.objects.count() == 1
    