from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsStaffOrReadOnly(BasePermission):
    """
    Custom permission to only allow staff users to edit it.
    Read permissions are allowed to any request, so we'll always allow GET, HEAD, or OPTIONS requests.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to staff users
        return request.user and request.user.is_authenticated and request.user.is_staff
