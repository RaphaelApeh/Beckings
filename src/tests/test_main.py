import pytest  # noqa

from django.urls import reverse


def test_health_check_view(client) -> None:

    response = client.get(reverse("health_check"))

    assert response.status_code == 200
    assert response.text.lower() == "Ok".lower()
