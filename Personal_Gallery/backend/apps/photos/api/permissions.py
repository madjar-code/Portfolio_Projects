from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission class that ensures:
    1. User is authenticated (view-level check)
    2. User owns the object (object-level check)
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated before accessing the view.
        This prevents AnonymousUser from reaching get_queryset().
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user owns the specific object.
        """
        return obj.user == request.user
