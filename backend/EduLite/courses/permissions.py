"""Custom permissions for the courses app."""

from rest_framework.permissions import BasePermission


class IsTeacherUser(BasePermission):
    """Allow access only to authenticated users marked as teachers."""

    message = "Only teachers can perform this action."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        profile = getattr(user, "profile", None)
        if not profile:
            return False

        return profile.occupation == "teacher"
