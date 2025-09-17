from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only the owner can edit/update/delete the note,
    others can only read.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are GET, HEAD, OPTIONS → anyone can read
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only the owner (uploaded_by) can modify
        return obj.uploader == request.user