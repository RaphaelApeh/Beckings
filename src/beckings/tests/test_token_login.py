from typing import TypeVar

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from rest_framework import status

from helpers._typing import AuthUser


UserType = TypeVar("UserType", AbstractUser, AuthUser)

User = get_user_model()


class TokenLoginTestCase(TestCase):


    def test_vaild_login(self) -> None:
        user_data = dict(username="testuser", password="password")
        User.objects.create_user(**user_data)
        data = {
            "username": "testuser",
            "password": "password"
        }
        response = self.client.post(reverse("api_login"), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
