from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission class to allow only admin users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'staff_profile') and 
            request.user.staff_profile.role == 'admin'
        )


class IsStaff(BasePermission):
    """
    Permission class to allow only staff users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'staff_profile') and 
            request.user.staff_profile.role == 'staff'
        )


class IsAdminOrStaff(BasePermission):
    """
    Permission class to allow both admin and staff users
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'staff_profile')
        )
