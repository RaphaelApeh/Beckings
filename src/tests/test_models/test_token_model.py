import pytest


@pytest.mark.django_db
class TestToken:


    def test_token_create(self, token, user) -> None:

        obj = token.objects.create(user=user)

        assert token.objects.filter(user=obj.user).exists()
    

    def test_token_indexes(self, token) -> None:

        assert "token_key_idx" in [ x.name for x in token._meta.indexes]

    

        