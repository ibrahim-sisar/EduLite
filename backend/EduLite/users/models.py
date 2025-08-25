# backend/EduLite/users/models.py
# Contains user profile models, friend request models, and privacy settings models

from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError

from typing import TYPE_CHECKING


from .models_choices import OCCUPATION_CHOICES, COUNTRY_CHOICES, LANGUAGE_CHOICES

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()

# Privacy Settings Choices
SEARCH_VISIBILITY_CHOICES = [
    ('everyone', 'Everyone'),
    ('friends_of_friends', 'Friends of Friends'),
    ('friends_only', 'Friends Only'),
    ('nobody', 'Nobody'),
]

PROFILE_VISIBILITY_CHOICES = [
    ('public', 'Public'),
    ('friends_only', 'Friends Only'),
    ('private', 'Private'),
]


class UserProfile(models.Model):
    # The signal in signals.py will create a UserProfile instance when a new User is created
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True, max_length=1000)
    occupation = models.CharField(
        max_length=64, choices=OCCUPATION_CHOICES, blank=True, null=True
    )
    country = models.CharField(
        max_length=64, choices=COUNTRY_CHOICES, blank=True, null=True
    )
    # the website can load auto-translated based on preferred language
    preferred_language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    # secondary language to fall back on
    secondary_language = models.CharField(
        max_length=64, choices=LANGUAGE_CHOICES, blank=True, null=True
    )
    picture = models.ImageField(
        upload_to="profile_pics", blank=True, null=True
    )  # Added null=True
    website_url = models.URLField(max_length=200, blank=True, null=True)

    friends = models.ManyToManyField(User, related_name="friend_profiles", blank=True)

    def clean(self):
        super().clean()  # Call parent clean()
        if self.preferred_language and self.secondary_language:
            if self.preferred_language == self.secondary_language:
                raise ValidationError({
                    'secondary_language': "Secondary language cannot be the same as the preferred language."
                })

    def __str__(self):
        ret_str = f"{self.user.username}"
        if self.user.first_name and self.user.last_name:
            ret_str += f" {self.user.first_name} {self.user.last_name}"
        elif self.user.first_name:
            ret_str += f" ({self.user.first_name})"
        elif self.user.last_name:
            ret_str += f" {self.user.last_name}"
        return f"{ret_str}"

    @property
    def teachers(self):
        """
        Returns a queryset of Users who are teachers of this user in any course.
        """
        return self.courses.filter(memberships__role='teacher').distinct().values_list('memberships__user', flat=True)

    @property
    def chatrooms(self):
        """
        Returns a queryset of ChatRooms that this user is a member of.
        """
        from chat.models import ChatRoom
        return ChatRoom.objects.filter(participants=self.user).values_list('id', flat=True)

    @property
    def courses(self):
        from courses.models import Course
        return Course.objects.filter(memberships__user=self.user).distinct()

class UserProfilePrivacySettings(models.Model):
    """
    Privacy settings for user profiles.
    Controls visibility, discoverability, and interaction permissions.

    The signal in signals.py will create a UserProfilePrivacySettings instance
    when a new UserProfile is created.
    """

    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="privacy_settings"
    )

    # Search and Discovery Settings
    search_visibility = models.CharField(
        max_length=20,
        choices=SEARCH_VISIBILITY_CHOICES,
        default='everyone',
        help_text="Who can find you in search results"
    )

    # Profile Information Visibility
    profile_visibility = models.CharField(
        max_length=20,
        choices=PROFILE_VISIBILITY_CHOICES,
        default='friends_only',  # Default to friends only
        help_text="Who can view your full profile details"
    )

    show_full_name = models.BooleanField(
        default=True,
        help_text="Show your first and last name in search results and profile"
    )

    show_email = models.BooleanField(
        default=False,
        help_text="Show your email address in your profile (not recommended)"
    )

    # Interaction Settings
    allow_friend_requests = models.BooleanField(
        default=True,
        help_text="Allow other users to send you friend requests"
    )

    allow_chat_invites = models.BooleanField(
        default=True,
        help_text="Allow other users to send you chat invitations"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile Privacy Settings"
        verbose_name_plural = "User Profile Privacy Settings"
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return f"Privacy settings for {self.user_profile.user.username}"

    def clean(self) -> None:
        """
        Validate privacy settings for logical consistency.
        """
        super().clean()

        # If search visibility is 'nobody', profile should be private or friends_only
        if self.search_visibility == 'nobody' and self.profile_visibility == 'public':
            raise ValidationError(
                "Profile cannot be public if search visibility is set to nobody."
            )

    def can_be_found_by_user(self, requesting_user: 'AbstractUser') -> bool:
        """
        Check if this user profile can be found in search by the requesting user.

        Args:
            requesting_user: The user performing the search

        Returns:
            bool: True if the profile should appear in search results
        """
        if not requesting_user or not requesting_user.is_authenticated:
            return self.search_visibility == 'everyone'

        # User can always find themselves
        if requesting_user == self.user_profile.user:
            return True

        if self.search_visibility == 'everyone':
            return True
        elif self.search_visibility == 'nobody':
            return False
        elif self.search_visibility == 'friends_only':
            # Optimized: Use exists() with direct query to avoid N+1
            return self.user_profile.friends.filter(id=requesting_user.id).exists()
        elif self.search_visibility == 'friends_of_friends':
            # Optimized: Use database-level joins to avoid N+1
            # First check if they are direct friends
            if self.user_profile.friends.filter(id=requesting_user.id).exists():
                return True

            # Check for mutual friends using optimized query
            # This uses a single query instead of fetching all friends
            # We need to check if any of user_profile's friends have requesting_user as a friend
            # user_profile.friends are User objects, and we need to check their profiles
            mutual_friends_exist = self.user_profile.friends.filter(
                profile__friends=requesting_user
            ).exists()
            
            return mutual_friends_exist

        return False

    def can_profile_be_viewed_by_user(self, requesting_user: 'AbstractUser') -> bool:
        """
        Check if the full profile can be viewed by the requesting user.

        Args:
            requesting_user: The user requesting to view the profile

        Returns:
            bool: True if the full profile can be viewed
        """
        if not requesting_user or not requesting_user.is_authenticated:
            return self.profile_visibility == 'public'

        # User can always view their own profile
        if requesting_user == self.user_profile.user:
            return True

        if self.profile_visibility == 'public':
            return True
        elif self.profile_visibility == 'private':
            return False
        elif self.profile_visibility == 'friends_only':
            # Optimized: Use exists() with direct query to avoid N+1
            return self.user_profile.friends.filter(id=requesting_user.id).exists()

        return False

    def can_receive_friend_request_from_user(self, requesting_user: 'AbstractUser') -> bool:
        """
        Check if this user can receive a friend request from the requesting user.

        Args:
            requesting_user: The user wanting to send a friend request

        Returns:
            bool: True if friend request can be sent
        """
        if not requesting_user or not requesting_user.is_authenticated:
            return False

        # Cannot send friend request to oneself
        if requesting_user == self.user_profile.user:
            return False

        # Check if friend requests are allowed
        if not self.allow_friend_requests:
            return False

        # Optimized: Check if they are already friends using exists()
        if self.user_profile.friends.filter(id=requesting_user.id).exists():
            return False

        # Optimized: Check if there's already a pending request using select_related
        existing_request = ProfileFriendRequest.objects.select_related('sender__user').filter(
            sender__user=requesting_user,
            receiver=self.user_profile
        ).exists()

        if existing_request:
            return False

        return True


# Example of how to get friend requests from a UserProfile:
# received_requests = my_profile.received_friend_requests.all()
# sent_requests = my_profile.sent_friend_requests.all()


class ProfileFriendRequest(models.Model):
    """
    Represents a friend request sent from one UserProfile to another.

    Methods:

    - accept(): Accepts the friend request. Deletes the request.
    - decline(): Declines the friend request. Deletes the request.
    """

    sender = models.ForeignKey(
        "UserProfile", on_delete=models.CASCADE, related_name="sent_friend_requests"
    )
    receiver = models.ForeignKey(
        "UserProfile", on_delete=models.CASCADE, related_name="received_friend_requests"
    )
    message = models.TextField(
        max_length=500, blank=True, null=True,
        help_text="Optional message to include with the friend request."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the friend request was sent."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"], name="unique_pending_friend_request"
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "Profile Friend Request"
        verbose_name_plural = "Profile Friend Requests"

    def __str__(self) -> str:
        return f"Friend request from {self.sender.user.username} to {self.receiver.user.username}"

    def clean(self) -> None:
        if self.sender == self.receiver:
            raise ValidationError("Cannot send a friend request to oneself.")
        # Optimized: Check if they are already friends using exists()
        if self.sender.friends.filter(id=self.receiver.user.id).exists():
            raise ValidationError("Cannot send a friend request to a friend.")
        if self.receiver.friends.filter(id=self.sender.user.id).exists():
            raise ValidationError("Cannot send a friend request to a friend.")
        super().clean()

    def accept(self) -> bool:
        """
        Accepts the friend request.
        Adds sender and receiver to each other's friends list and deletes the request.
        """
        try:
            with transaction.atomic():
                # Re-fetch with `select_for_update` to guard against races
                # Include select_related to prevent additional queries during friend additions
                req = type(self).objects.select_for_update().select_related(
                    'sender__user', 
                    'receiver__user'
                ).get(pk=self.pk)
                req.receiver.friends.add(req.sender.user)
                req.sender.friends.add(req.receiver.user)
                req.delete()
            return True
        except (type(self).DoesNotExist, IntegrityError):
            return False

    def decline(self) -> bool:
        """
        Declines the friend request.
        Deletes the request.
        """
        try:
            with transaction.atomic():
                # Re-fetch with `select_for_update` to guard against races
                req = type(self).objects.select_for_update().get(pk=self.pk)
                req.delete()
            return True
        except (type(self).DoesNotExist, IntegrityError):
            return False


class FriendSuggestion(models.Model):
    """ Represents a suggested friend for a user based on various criteria."""
    user = models.ForeignKey(
        User,
        related_name="friend_suggestions",
        on_delete=models.CASCADE
    )
    suggested_user = models.ForeignKey(
        User,
        related_name="suggested_to",
        on_delete=models.CASCADE
    )
    score = models.FloatField()
    reason = models.CharField(max_length=255)  # e.g., "3 mutual friends", "Recently messaged in Study Group"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'suggested_user')
