from rest_framework import permissions

class UpdateOwnProfile(permissions.BasePermission):
    """Restrict user to edit their own profile"""

    def has_object_permission(self, request, view, obj):
        """Check user has permission for put request"""
        if request.method in permissions.SAFE_METHODS:
            print(request.method)
            print(permissions.SAFE_METHODS)
            return True
        
        return request.user.id==obj.id