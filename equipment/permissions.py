from rest_framework import permissions

class IsAdminGroupUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if user is an ad1min user
        is_admin_user = request.user and request.user.is_staff

        # Check if user is in the admin group
        is_in_admin_group = request.user and request.user.groups.filter(name='Admin').exists()

        # Allow if user is an admin user or in the admin group
        return is_admin_user or is_in_admin_group
    
class IsMemberGroupUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if user is an ad1min user
        is_admin_user = request.user and request.user.is_staff

        # Check if user is in the member group
        is_in_member_group = request.user and request.user.groups.filter(name='Member').exists()

        # Check if user is in the admin group
        is_in_admin_group = request.user and request.user.groups.filter(name='Admin').exists()

        # Allow if user is an admin user or in the member group
        return is_admin_user or is_in_admin_group or is_in_member_group