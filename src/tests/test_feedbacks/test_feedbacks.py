from http import HTTPStatus

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from feedbacks.models import FeedBack


UserModel = get_user_model()

def test_anonymous_user_feedback(client):

    data = {
        "email": "testuser@test.com",
        "complain": "The site navbar is duplicated in the home page",
        "complain_type": "site"
    }
    initial_count = FeedBack.objects.count()
    response = client.post(reverse("feedback"), data)
    assert response.status_code == HTTPStatus.OK
    assert (initial_count + 1) > initial_count


def test_authenticated_user_feedback(client):
    user = UserModel.objects.create_user(
        username="testuser",
        password="test@secrete"
    )
    client.force_login(user)
    data = {
        "user": user,
        "complain": "The site navbar is duplicated in the home page",
        "complain_type": "site"
    }
    initial_count = FeedBack.objects.count()
    response = client.post(reverse("feedback"), data)
    assert response.status_code == HTTPStatus.OK
    assert (initial_count + 1) > initial_count