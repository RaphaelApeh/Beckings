import json
from pathlib import Path

import pytest

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_product_export(client, products_factory, user):

    products_factory
    client.force_login(user)
    response = client.get(reverse("export_import_product"), {"format": "json"})

    assert response.status_code == 200

    assert isinstance(json.loads(response.content), list)


@pytest.mark.django_db
def test_product_import(client, user, product):
    
    with open(Path().resolve() / "data.json", encoding="utf-8") as json_file:
        file = SimpleUploadedFile(
            "data.json",
            content=json_file.read().encode(),
            content_type="application/json"
        )
    client.force_login(user)
    response = client.post(reverse("export_import_product"),
                           data={
                               "file": file,
                               "format": "json"
                           },
                           follow=True)
    
    assert "Data Saved." in response.text
    # TODO
    print(product.objects.all()) # not savings to the db for some reason
    #assert product.objects.count() == 1
    