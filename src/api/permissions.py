from rest_framework import permissions


class IsUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj) -> bool:
        
        return bool(request.user.is_authenticated and obj == request.user or request.user.is_staff)