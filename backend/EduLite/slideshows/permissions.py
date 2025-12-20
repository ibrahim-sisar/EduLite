"""Custom permissions for the slideshows app."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Allow owners full access, others read-only for public/unlisted content.

    - Owner: Full access to their slideshows (read, write, delete)
    - Others: Read-only access if slideshow is published AND (public or unlisted)
    - Private slideshows: Only owner can access
    """

    message = "You do not have permission to modify this slideshow."

    def has_object_permission(self, request, view, obj):
        """Check if user can access the slideshow object."""
        # Get the slideshow (could be Slide or Slideshow object)
        slideshow = obj if hasattr(obj, "visibility") else obj.slideshow

        # Owner always has full access
        if slideshow.created_by == request.user:
            return True

        # Read-only access for safe methods
        if request.method in SAFE_METHODS:
            # Must be published AND (public or unlisted)
            if not slideshow.is_published:
                return False
            return slideshow.visibility in ["public", "unlisted"]

        # Write permissions only for owner
        return False


class IsOwner(BasePermission):
    """
    Allow only the owner to access.
    Used for operations that should be strictly owner-only.
    """

    message = "Only the owner can perform this action."

    def has_object_permission(self, request, view, obj):
        """Check if user is the owner."""
        # Get the slideshow (could be Slide or Slideshow object)
        slideshow = obj if hasattr(obj, "created_by") else obj.slideshow
        return slideshow.created_by == request.user


class CanViewSlideshow(BasePermission):
    """
    Check if user can view a slideshow based on visibility settings.

    - Owner: Can always view their own slideshows
    - Others: Can view if published AND (public or unlisted)
    - Private: Only owner can view
    """

    message = "You do not have permission to view this slideshow."

    def has_object_permission(self, request, view, obj):
        """Check if user can view the slideshow."""
        # Get the slideshow (could be Slide or Slideshow object)
        slideshow = obj if hasattr(obj, "visibility") else obj.slideshow

        # Owner can always view
        if slideshow.created_by == request.user:
            return True

        # Others: must be published AND (public or unlisted)
        if not slideshow.is_published:
            return False

        return slideshow.visibility in ["public", "unlisted"]
