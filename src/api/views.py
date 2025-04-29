from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

from decorators import paginate
from helpers import UserSerializer

User = get_user_model()


@api_view(["GET"])
@paginate(PageNumberPagination, page_size=2)
def users_list_view(request):
    users = User.objects.all()
    return users, UserSerializer(users, many=True).data