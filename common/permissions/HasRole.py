from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_roles = getattr(view, "allowed_roles", [])
        return request.user.role in allowed_roles
