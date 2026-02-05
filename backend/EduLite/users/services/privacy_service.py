"""
Privacy Service - Centralized privacy and visibility logic.

This service consolidates all privacy-related business logic that was previously
scattered across models.py and serializers.py. It provides a single source of
truth for privacy rules, making them easier to audit, test, and maintain.

Usage:
    from users.services import PrivacyService

    # Check if user can be found in search
    can_find = PrivacyService.can_be_found_by_user(privacy_settings, requesting_user)

    # Check if profile can be viewed
    can_view = PrivacyService.can_view_full_profile(privacy_settings, requesting_user)

    # Check field visibility
    show_email = PrivacyService.should_show_email(user, requesting_user)
"""

from typing import TYPE_CHECKING, Optional, Set

from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from users.models import UserProfile, UserProfilePrivacySettings

# Use the actual User model for type hints to avoid mypy errors
User = get_user_model()


class PrivacyService:
    """
    Centralized service for all privacy and visibility logic.

    All methods are static since privacy checks don't require instance state.
    This makes the service easy to test and use without instantiation.
    """

    # =========================================================================
    # Search Visibility
    # =========================================================================

    @staticmethod
    def can_be_found_by_user(
        privacy_settings: "UserProfilePrivacySettings",
        requesting_user: Optional[User],  # type: ignore[valid-type]
    ) -> bool:
        """
        Check if a user profile can be found in search by the requesting user.

        Args:
            privacy_settings: The target user's privacy settings
            requesting_user: The user performing the search (None if anonymous)

        Returns:
            bool: True if the profile should appear in search results
        """
        # Anonymous users can only find profiles with "everyone" visibility
        if not requesting_user or not requesting_user.is_authenticated:
            return privacy_settings.search_visibility == "everyone"

        # User can always find themselves
        if requesting_user == privacy_settings.user_profile.user:
            return True

        visibility = privacy_settings.search_visibility

        if visibility == "everyone":
            return True
        elif visibility == "nobody":
            return False
        elif visibility == "friends_only":
            return privacy_settings.user_profile.friends.filter(
                id=requesting_user.id
            ).exists()
        elif visibility == "friends_of_friends":
            # First check if they are direct friends
            if privacy_settings.user_profile.friends.filter(
                id=requesting_user.id
            ).exists():
                return True

            # Check for mutual friends using optimized query
            return PrivacyService.have_mutual_friends(
                privacy_settings.user_profile, requesting_user
            )

        return False

    # =========================================================================
    # Profile Visibility
    # =========================================================================

    @staticmethod
    def can_view_full_profile(
        privacy_settings: "UserProfilePrivacySettings",
        requesting_user: Optional[User],  # type: ignore[valid-type]
    ) -> bool:
        """
        Check if the full profile can be viewed by the requesting user.

        Args:
            privacy_settings: The target user's privacy settings
            requesting_user: The user requesting to view the profile (None if anonymous)

        Returns:
            bool: True if the full profile can be viewed
        """
        # Anonymous users can only view public profiles
        if not requesting_user or not requesting_user.is_authenticated:
            return privacy_settings.profile_visibility == "public"

        # User can always view their own profile
        if requesting_user == privacy_settings.user_profile.user:
            return True

        # Admin/staff can view all profiles
        if requesting_user.is_superuser or requesting_user.is_staff:
            return True

        visibility = privacy_settings.profile_visibility

        if visibility == "public":
            return True
        elif visibility == "private":
            return False
        elif visibility == "friends_only":
            return privacy_settings.user_profile.friends.filter(
                id=requesting_user.id
            ).exists()

        return False

    # =========================================================================
    # Friend Request Permissions
    # =========================================================================

    @staticmethod
    def can_receive_friend_request(
        privacy_settings: "UserProfilePrivacySettings",
        requesting_user: Optional[User],  # type: ignore[valid-type]
    ) -> bool:
        """
        Check if this user can receive a friend request from the requesting user.

        Args:
            privacy_settings: The target user's privacy settings
            requesting_user: The user wanting to send a friend request

        Returns:
            bool: True if friend request can be sent
        """
        # Must be authenticated
        if not requesting_user or not requesting_user.is_authenticated:
            return False

        # Cannot send friend request to oneself
        if requesting_user == privacy_settings.user_profile.user:
            return False

        # Check if friend requests are allowed
        if not privacy_settings.allow_friend_requests:
            return False

        # Check if they are already friends
        if privacy_settings.user_profile.friends.filter(id=requesting_user.id).exists():
            return False

        # Check if there's already a pending request
        # Import here to avoid circular imports
        from users.models import ProfileFriendRequest

        existing_request = ProfileFriendRequest.objects.filter(
            sender__user=requesting_user, receiver=privacy_settings.user_profile
        ).exists()

        if existing_request:
            return False

        return True

    # =========================================================================
    # Field-Level Visibility
    # =========================================================================

    @staticmethod
    def should_show_email(
        user: User,  # type: ignore[valid-type]
        requesting_user: Optional[User],  # type: ignore[valid-type]
    ) -> bool:
        """
        Determine if email should be shown to the requesting user.

        Args:
            user: The user whose email visibility is being checked
            requesting_user: The user requesting to see the email

        Returns:
            bool: True if email should be visible
        """
        # User can always see their own email
        if requesting_user and user.pk == requesting_user.pk:
            return True

        # Admin users can see all emails
        if requesting_user and (
            requesting_user.is_superuser or requesting_user.is_staff
        ):
            return True

        # Check privacy settings
        privacy_settings = PrivacyService._get_privacy_settings(user)
        if privacy_settings:
            return privacy_settings.show_email

        # Default to hiding email if no privacy settings exist
        return False

    @staticmethod
    def should_show_full_name(
        user: User,  # type: ignore[valid-type]
        requesting_user: Optional[User],  # type: ignore[valid-type]
    ) -> bool:
        """
        Determine if full name should be shown to the requesting user.

        Args:
            user: The user whose name visibility is being checked
            requesting_user: The user requesting to see the name

        Returns:
            bool: True if full name should be visible
        """
        # User can always see their own name
        if requesting_user and user.pk == requesting_user.pk:
            return True

        # Admin users can see all names
        if requesting_user and (
            requesting_user.is_superuser or requesting_user.is_staff
        ):
            return True

        # Check privacy settings
        privacy_settings = PrivacyService._get_privacy_settings(user)
        if privacy_settings:
            return privacy_settings.show_full_name

        # Default to showing names if no privacy settings exist
        return True

    @staticmethod
    def get_visible_fields(
        user: User,  # type: ignore[valid-type]
        requesting_user: Optional[User],  # type: ignore[valid-type]
    ) -> Set[str]:
        """
        Return the set of profile fields that the requesting user is allowed to see.

        Args:
            user: The user whose profile fields are being checked
            requesting_user: The user requesting to view the fields

        Returns:
            Set[str]: Set of field names that should be visible
        """
        # Base fields always visible
        visible = {"url", "username", "profile_url"}

        # Check email visibility
        if PrivacyService.should_show_email(user, requesting_user):
            visible.add("email")

        # Check name visibility
        if PrivacyService.should_show_full_name(user, requesting_user):
            visible.update({"first_name", "last_name", "full_name"})

        return visible

    # =========================================================================
    # Helper Methods
    # =========================================================================

    @staticmethod
    def have_mutual_friends(
        user_profile: "UserProfile",
        other_user: User,  # type: ignore[valid-type]
    ) -> bool:
        """
        Check if two users have mutual friends.

        Uses an optimized database query to avoid N+1 problems.

        Args:
            user_profile: The first user's profile
            other_user: The second user

        Returns:
            bool: True if they have at least one mutual friend
        """
        # Check if any of user_profile's friends have other_user as a friend
        return user_profile.friends.filter(profile__friends=other_user).exists()

    @staticmethod
    def get_user_friends_ids(user: User) -> Set[int]:  # type: ignore[valid-type]
        """
        Get the set of friend IDs for a user.

        Useful for batch operations where you need to check friend status
        for multiple users without repeated queries.

        Args:
            user: The user whose friends to retrieve

        Returns:
            Set[int]: Set of user IDs who are friends with this user
        """
        if not user or not user.is_authenticated:
            return set()

        try:
            return set(user.profile.friends.values_list("id", flat=True))
        except AttributeError:
            return set()

    @staticmethod
    def _get_privacy_settings(
        user: User,  # type: ignore[valid-type]
    ) -> Optional["UserProfilePrivacySettings"]:
        """
        Get privacy settings for a user.

        Args:
            user: The user whose privacy settings to retrieve

        Returns:
            UserProfilePrivacySettings or None if not found
        """
        try:
            if hasattr(user, "profile") and hasattr(user.profile, "privacy_settings"):
                return user.profile.privacy_settings
        except AttributeError:
            pass
        return None
