# users/permissions.py

from rest_framework import permissions
from .models import UserProfile, ProfileFriendRequest

class IsProfileOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a UserProfile or admins to edit it.
    Read access (GET, HEAD, OPTIONS) is allowed for any authenticated user.
    """

    def has_permission(self, request, view) -> bool:
        # This initial check ensures the user is authenticated before has_object_permission is called.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj: UserProfile) -> bool:
        """
        'obj' here is the UserProfile instance.
        """
        # Read permissions are allowed for any authenticated request if they passed has_permission.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed if the user is the owner of the profile
        # or if the user is an admin.
        return obj.user == request.user or request.user.is_staff


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for the core User model.
    - Allows admins to perform any action.
    - Allows authenticated users to view (GET) any user's details (can be tightened if needed).
    - Allows a user to update (PUT, PATCH) or delete (DELETE) their own User record.
    """

    def has_permission(self, request, view) -> bool:
        # Ensure the user is authenticated for any operation.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        """
        'obj' here is the User instance (e.g., from get_user_model()).
        """
        # Admins (staff users) can do anything.
        if request.user.is_staff:
            return True

        # For non-admins:
        # If it's a safe method (GET, HEAD, OPTIONS), allow access.
        if request.method in permissions.SAFE_METHODS:
            return True

        # For unsafe methods (PUT, PATCH, DELETE), the user must be the object itself.
        return obj == request.user
    
    
class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to any authenticated user,
    but write/delete access only to admin users.
    """

    def has_permission(self, request, view) -> bool:
        # First, ensure the user is authenticated for any access.
        if not request.user or not request.user.is_authenticated:
            return False

        # Read permissions are allowed to any authenticated user (GET, HEAD or OPTIONS requests).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (POST, PUT, PATCH, DELETE) are only allowed to admin users.
        return request.user.is_staff


## -- Friend Request Permissions -- ##


class IsFriendRequestReceiver(permissions.BasePermission):
    """
    Allows access only if the request.user.profile is the receiver of the ProfileFriendRequest.
    """
    def has_object_permission(self, request, view, obj: ProfileFriendRequest): 
        if hasattr(request.user, 'profile'):
            return obj.receiver == request.user.profile
        return False


class IsFriendRequestReceiverOrSender(permissions.BasePermission):
    """
    Custom permission to only allow the receiver or the sender of a friend request
    to perform an action on it (e.g., decline or cancel).
    """
    message = "You do not have permission to perform this action on this friend request."

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, ProfileFriendRequest):
            return False 

        # Check if the request.user has a 'profile' attribute
        if not hasattr(request.user, 'profile'):
            return False

        user_profile = request.user.profile
        return obj.receiver == user_profile or obj.sender == user_profile
