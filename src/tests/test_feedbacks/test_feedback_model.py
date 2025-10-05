from django.contrib.auth import get_user_model

from feedbacks.models import FeedBack
from helpers.testing import create_factory


UserModel = get_user_model()

@create_factory("helpers.factories.UserFactory")
def test_feedback_model():
    user = UserModel.objects.first()
    kwargs = {
        "complain": "Hello World",
        "complain_type": "other"
    }
    user_, obj = FeedBack.objects.create_for_user(user, **kwargs)
    assert all([user_, obj])
    assert user == user_
    count = FeedBack.objects.count()
    obj.delete()
    assert FeedBack.objects.count() < count