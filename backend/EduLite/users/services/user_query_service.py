"""
User Query Service - Centralized cross-app query logic.

Isolates queries that span multiple apps (users, courses, chat)
to avoid circular dependencies in models.

Usage:
    from users.services import UserQueryService

    # Get user's courses
    courses = UserQueryService.get_user_courses(user)

    # Get user's course IDs
    course_ids = UserQueryService.get_user_course_ids(user)

    # Get user's teachers
    teacher_ids = UserQueryService.get_user_teacher_ids(user)

    # Get user's chatroom IDs
    chatroom_ids = UserQueryService.get_user_chatroom_ids(user)
"""

from typing import TYPE_CHECKING, Set

from django.db.models import QuerySet

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class UserQueryService:
    """
    Centralized service for cross-app user queries.

    Contains queries that would otherwise create circular dependencies
    between the users app and other apps (courses, chat).

    All methods are static since they don't require instance state.
    """

    # =========================================================================
    # Course Queries
    # =========================================================================

    @staticmethod
    def get_user_courses(user: "User") -> QuerySet:
        """
        Get all courses a user is a member of.

        Args:
            user: The user to get courses for

        Returns:
            QuerySet of Course objects
        """
        from courses.models import Course

        return Course.objects.filter(memberships__user=user).distinct()

    @staticmethod
    def get_user_course_ids(user: "User") -> Set[int]:
        """
        Get IDs of all courses a user is a member of.

        Args:
            user: The user to get course IDs for

        Returns:
            Set of course IDs
        """
        return set(user.course_memberships.values_list("course_id", flat=True))

    # =========================================================================
    # Teacher Queries
    # =========================================================================

    @staticmethod
    def get_user_teacher_ids(user: "User") -> Set[int]:
        """
        Get IDs of all teachers for courses the user is enrolled in.

        This finds all users with the "teacher" role in any course
        where the given user is a member.

        Args:
            user: The user to get teachers for

        Returns:
            Set of user IDs who are teachers of this user's courses
        """
        from courses.models import CourseMembership

        course_ids = user.course_memberships.values_list("course_id", flat=True)
        return set(
            CourseMembership.objects.filter(
                course_id__in=course_ids, role="teacher"
            ).values_list("user_id", flat=True)
        )

    # =========================================================================
    # Chatroom Queries
    # =========================================================================

    @staticmethod
    def get_user_chatroom_ids(user: "User") -> Set[int]:
        """
        Get IDs of all chatrooms the user is a participant of.

        Args:
            user: The user to get chatroom IDs for

        Returns:
            Set of chatroom IDs
        """
        from chat.models import ChatRoom

        return set(
            ChatRoom.objects.filter(participants=user).values_list("id", flat=True)
        )

    @staticmethod
    def get_user_chatrooms(user: "User") -> QuerySet:
        """
        Get all chatrooms the user is a participant of.

        Args:
            user: The user to get chatrooms for

        Returns:
            QuerySet of ChatRoom objects
        """
        from chat.models import ChatRoom

        return ChatRoom.objects.filter(participants=user)
