from rest_framework import permissions
from django.contrib.auth import get_user_model


User = get_user_model()


class IsUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj) -> bool:

        match obj:
            case s if isinstance(s, User):
                return bool(
                    request.user.is_authenticated
                    and obj == request.user
                    or request.user.is_staff
                )
            case f if hasattr(f, "user"):
                return bool(
                    request.user.is_authenticated
                    and obj.user == request.user
                    or request.user.is_staff
                )
            case _:
                return False
