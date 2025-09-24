from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status


User = get_user_model()


def test_change_password_view(authenticated_client, user) -> None:

    data = {
        "old_password": "password",
        "new_password": "sjsoddjso",  # valid password
        "confirmation_password": "sjsoddjso",
    }
    response = authenticated_client.post(reverse("user-change-password"), data)

    assert response.status_code == 200
    assert response.data["success"] == "Password set Successfully."
    assert user.check_password(data["new_password"])


def test_invalid_change_password_view(authenticated_client, user) -> None:

    data = {
        "old_password": "password",
        "new_password": "password1",  # invalid password
        "confirmation_password": "password1",
    }
    response = authenticated_client.post(reverse("user-change-password"), data)

    assert response.status_code == 404
    assert "This password is too common." == response.data["detail"]


def test_user_create_api_endpoint(api_client) -> None:

    data = {
        "username": "johndoe",
        "email": "johndoe@test.com",
        "password1": "a_strong_password",
        "password2": "a_strong_password",
    }
    response = api_client.post(reverse("user-list"), data)
    qs = User.objects.filter(username=data["username"])

    assert response.status_code == 201
    assert data["username"] == response.data["user"]["username"]
    assert qs.exists()


def test_user_delete_api_endpoint(api_client) -> None:

    user = User.objects.create_user("hello_world", password="bad_password")
    api_client.force_authenticate(user=user)

    response = api_client.delete(reverse("user-detail", args=(user.pk,)))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(pk=user.pk).exists()


def test_user_update_api_endpoint(api_client) -> None:

    data = {
        "username": "johndoe",
        "email": "johndoe@test.com",
        "password1": "a_strong_password",
        "password2": "a_strong_password",
    }
    response = api_client.post(reverse("user-list"), data)
    qs = User.objects.filter(username=data["username"])

    assert qs.exists()
    assert len(qs) == 1
    assert response.status_code == status.HTTP_201_CREATED

    user = qs.get()
    api_client.force_authenticate(user=user)
    updated_data = {"username": "johnsmith"}
    response = api_client.put(reverse("user-detail", args=(user.pk,)), updated_data)

    user.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert user.username == updated_data["username"]
    assert "details updated." in response.data.get("message")
