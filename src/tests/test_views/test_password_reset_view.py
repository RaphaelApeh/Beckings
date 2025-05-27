import pytest

from django.core import mail
from django.urls import reverse


@pytest.mark.django_db
class TestPasswordResetView:

    def test_forgot_password(self, client, user) -> None:

        response = client.get(reverse("password_reset"))

        assert response.status_code == 200
        assert "Password Reset" in response.text

        assert user.email is not None
        response = client.post(reverse("password_reset"), {"email": user.email})

        assert response.status_code == 302
        assert len(mail.outbox) == 1
        assert "Password Reset Sent" in mail.outbox[0].subject


