"""Custom permissions for the courses app."""

from django.conf import settings
from rest_framework.permissions import BasePermission

from .models import CourseMembership


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


class CanCreateCourse(BasePermission):
    """
    Allow course creation based on the COURSE_CREATION_REQUIRES_TEACHER setting.

    When True (default): only users with profile.occupation == "teacher" can create.
    When False: any authenticated user can create.
    """

    message = "You do not have permission to create courses."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        if not getattr(settings, "COURSE_CREATION_REQUIRES_TEACHER", True):
            return True

        profile = getattr(user, "profile", None)
        if not profile:
            return False

        return profile.occupation == "teacher"


class IsCourseTeacher(BasePermission):
    """
    Object-level permission: user must be a teacher in the course.

    For views with a course pk in the URL, checks has_permission directly.
    For detail views, checks has_object_permission on the course object.
    """

    message = "Only course teachers can perform this action."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        course_pk = view.kwargs.get("pk")
        if course_pk is not None:
            return CourseMembership.objects.filter(
                user=user,
                course_id=course_pk,
                role="teacher",
                status="enrolled",
            ).exists()

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        course = obj if hasattr(obj, "visibility") else getattr(obj, "course", obj)
        return CourseMembership.objects.filter(
            user=user,
            course=course,
            role="teacher",
            status="enrolled",
        ).exists()


class IsCourseMember(BasePermission):
    """
    Object-level permission: user must be an enrolled member of the course.
    """

    message = "You must be a course member to perform this action."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        course_pk = view.kwargs.get("pk")
        if course_pk is not None:
            return CourseMembership.objects.filter(
                user=user,
                course_id=course_pk,
                status="enrolled",
            ).exists()

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False

        course = obj if hasattr(obj, "visibility") else getattr(obj, "course", obj)
        return CourseMembership.objects.filter(
            user=user,
            course=course,
            status="enrolled",
        ).exists()
