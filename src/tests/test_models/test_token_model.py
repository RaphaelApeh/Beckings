import pytest
import time_machine

from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestToken:

    def test_token_create(self, token, user) -> None:

        obj = token.objects.create(user=user)

        assert token.objects.filter(user=obj.user).exists()

    def test_token_indexes(self, token) -> None:

        assert "token_key_idx" in [x.name for x in token._meta.indexes]

    def test_user_created_token(self, token, settings) -> None:

        user = User.objects.create_user(username="1testuser", password="tokenpassword")
        obj = token.objects.create(user=user)

        assert obj is not None
        assert isinstance(obj.key, str)
        assert len(obj.key) >= 40

    def test_token_expiration(self, token, settings) -> None:

        user = User.objects.create_user(username="1testuser", password="tokenpassword")
        obj = token.objects.create(user=user)

        assert hasattr(obj, "is_expired")

        with time_machine.travel(
            timezone.now() + settings.API_TOKEN_EXPIRE_TIME
        ):  # travel 2 days
            assert obj.is_expired()

        with time_machine.travel(timezone.now() + timezone.timedelta(days=1)):
            assert not obj.is_expired()

        assert not obj.is_expired()

    def test_token_invalid(self, token) -> None:

        user = User.objects.create_user(username="1testuser", password="tokenpassword")
        obj = token.objects.create(user=user)
        token_key = obj.key
        user.delete()

        with pytest.raises(obj.DoesNotExist):
            token.objects.get(key=token_key)
