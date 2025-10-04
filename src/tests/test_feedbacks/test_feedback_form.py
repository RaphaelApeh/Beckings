import pytest
from django.contrib.auth import get_user_model

from feedbacks.forms import FeedBackForm
from feedbacks.models import FeedBack
from helpers.testing import create_factory


UserModel = get_user_model()

def test_form_with_email():
    data = {
        "email": "testuser@gmail.com",
        "complain": "THis test suite is nice",
        "complain_type": "other"
    }
    form = FeedBackForm(data=data)
    assert form.is_valid()
    user, obj = form.save()
    assert user is None and obj is not None

@create_factory("helpers.factories.UserFactory")
def test_form_with_user():
    user = UserModel.objects.first()
    count = FeedBack.objects.count()
    data = {
        "user": user,
        "complain": "THis test suite is nice",
        "complain_type": "other"
    }
    form = FeedBackForm(data)
    assert form.is_valid()
    user, obj = form.save()
    assert user is not None and obj is not None
    assert FeedBack.objects.count() > count


@create_factory("helpers.factories.UserFactory")
def test_form_with_initial():
    user = UserModel.objects.first()
    data = {
        "complain": "THis test suite is nice",
        "complain_type": "other"
    }
    form = FeedBackForm(data, initial={"user": user})
    assert form.is_valid()
    user, obj = form.save()
    assert user is not None and obj is not None

