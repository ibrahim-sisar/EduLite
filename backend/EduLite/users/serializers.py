from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.urls import reverse
from typing import Optional, TYPE_CHECKING

from rest_framework import serializers

from .models import (
    UserProfile, ProfileFriendRequest, UserProfilePrivacySettings,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


# -- Profile Serializers -- ##


class ProfileSerializer(
    serializers.HyperlinkedModelSerializer
):  # Or HyperlinkedModelSerializer if you prefer
    """
    Serializer for the UserProfile model.
    Privacy-aware serializer that respects UserProfilePrivacySettings.
    """

    user_url = serializers.HyperlinkedRelatedField(
        source="user",
        view_name="user-detail",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "url",  # URL for the UserProfile instance itself
            "user_url",  # URL for the related User instance
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

    def _get_requesting_user(self) -> Optional['AbstractUser']:
        """Get the requesting user from context."""
        request = self.context.get('request')

        # Production: Get authenticated user from request
        if request and hasattr(
            request, 'user'
        ) and hasattr(
            request.user, 'is_authenticated'
        ) and request.user.is_authenticated:
            return request.user

        # Test context: Allow passing user directly (only for tests)
        test_user = self.context.get('test_user')
        if test_user and hasattr(test_user, 'pk'):
            return test_user

        return None

    def _can_view_full_profile(
        self, obj: UserProfile, requesting_user: Optional['AbstractUser']
    ) -> bool:
        """
        Check if the requesting user can view the
        full profile based on privacy settings.
        """
        if not requesting_user:
            return False

        # User can always view their own profile
        if requesting_user.pk == obj.user.pk:
            return True

        # Admin users can view all profiles
        if requesting_user.is_superuser or requesting_user.is_staff:
            return True

        # Check privacy settings with proper error handling
        try:
            privacy_settings = getattr(obj, 'privacy_settings', None)
            if privacy_settings:
                return privacy_settings.can_profile_be_viewed_by_user(
                    requesting_user
                )
        except (AttributeError, UserProfilePrivacySettings.DoesNotExist):
            pass

        # Default to friends_only if no privacy settings exist
        return obj.friends.filter(pk=requesting_user.pk).exists()

    def to_representation(self, instance):
        """
        Override to apply privacy filtering based on profile visibility settings.
        """
        representation = super().to_representation(instance)
        requesting_user = self._get_requesting_user()

        # Check if requesting user can view the full profile
        if not self._can_view_full_profile(instance, requesting_user):
            # For users who can't view the full profile, return limited info
            limited_fields = ['url', 'user_url']
            representation = {
                key: value for key, value in representation.items() if key in limited_fields
            }

        return representation


# -- User/Group Hyperlinked Serializers -- ##


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Group model.
    Exposes the 'url' (hyperlink to the group detail) and 'name' of the group.
    """

    class Meta:
        model = Group
        fields = ["id", "url", "name"]
        # 'url' is automatically configured by HyperlinkedModelSerializer


class UserSerializer(serializers.HyperlinkedModelSerializer):  # Or ModelSerializer
    """
    Serializer for the User model, now including nested profile information.
    Privacy-aware serializer that respects UserProfilePrivacySettings.
    """

    profile_url = serializers.HyperlinkedRelatedField(
        source="profile",
        view_name="userprofile-detail",
        read_only=True,
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "url",  # URL for the User instance itself
            "profile_url",  # URL for the UserProfile instance
            "username",
            "email",
            "groups",
            "first_name",
            "last_name",
            "full_name",
        ]

    def get_full_name(self, obj):
        first = obj.first_name
        last = obj.last_name
        if first and last:
            return f"{first} {last}"
        elif first:
            return first
        elif last:
            return last
        return ""

    # In UserSerializer class
    def _get_requesting_user(self):
        """Get the requesting user from context."""
        request = self.context.get('request')

        # Production: Get authenticated user from request
        if request and hasattr(
            request, 'user'
        ) and hasattr(
            request.user, 'is_authenticated'
        ) and request.user.is_authenticated:
            return request.user

        # Test context: Allow passing user directly (only for tests)
        test_user = self.context.get('test_user')  # Doesn't exist without test
        if test_user and hasattr(test_user, 'pk'):
            return test_user

        return None

    def _should_show_email(self, obj, requesting_user: Optional['AbstractUser']) -> bool:
        """
        Determine if email should be shown to the requesting user.
        """
        # User can always see their own email - use pk comparison
        if requesting_user and obj.pk == requesting_user.pk:
            return True

        # Admin users can see all emails
        if requesting_user and (requesting_user.is_superuser or requesting_user.is_staff):
            return True

        # Check privacy settings
        try:
            if hasattr(obj, 'profile') and hasattr(obj.profile, 'privacy_settings'):
                privacy_settings = obj.profile.privacy_settings
                return privacy_settings.show_email
        except (AttributeError, UserProfilePrivacySettings.DoesNotExist):
            pass

        # Default to hiding email if no privacy settings exist
        return False

    def _should_show_full_name(self, obj, requesting_user: Optional['AbstractUser']) -> bool:
        """
        Determine if full name should be shown to the requesting user.
        """
        # User can always see their own name - fix the comparison
        if requesting_user and obj.id == requesting_user.id:
            return True

        # Admin users can see all names
        if requesting_user and (requesting_user.is_superuser or requesting_user.is_staff):
            return True

        # Check privacy settings with proper Django ORM access
        try:
            if hasattr(obj, 'profile') and hasattr(obj.profile, 'privacy_settings'):
                privacy_settings = obj.profile.privacy_settings
                return privacy_settings.show_full_name
        except AttributeError:
            pass

        # Default to showing names if no privacy settings exist
        return True

    def to_representation(self, instance):
        """
        Override to apply privacy filtering based on individual field privacy settings.
        """
        representation = super().to_representation(instance)
        requesting_user = self._get_requesting_user()

        # Apply individual field privacy filtering
        if not self._should_show_email(instance, requesting_user):
            representation.pop('email', None)

        if not self._should_show_full_name(instance, requesting_user):
            representation.pop('first_name', None)
            representation.pop('last_name', None)
            representation.pop('full_name', None)

        return representation



## -- Secure Password Hashing Serializers -- ##


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles username, email, password input, password confirmation, and secure password hashing.
    """

    email = serializers.EmailField(required=True)

    password = serializers.CharField(
        write_only=True,  # ensures the password is never returned in the response
        required=True,
        validators=[validate_password],  # validates that the password is strong enough
    )
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm password"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            # If we want users to optionally enter their names on registration:
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value: str) -> str:
        """
        Perform custom email validations:
        1. Check for blocked domains.
        2. Check for email uniqueness.
        """
        if "@" not in value:
            # This is an extra safeguard. EmailField should catch most format issues.
            raise serializers.ValidationError(
                "Invalid email format: '@' symbol missing."
            )
        email_name, domain_part = value.split("@", 1)
        from django.conf import settings

        blocked_domains = getattr(
            settings, "BLOCKED_EMAIL_DOMAINS", ["example.com", "test.com"]
        )

        if domain_part.lower() in [d.lower() for d in blocked_domains]:
            raise serializers.ValidationError(
                "Registration from this email domain is not allowed."
            )

        # Uniqueness Check
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )

        return value  # If all checks pass, return the validated email value

    def validate_username(self, value):
        """
        Check that the username is unique.
        """
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate(self, attrs):
        """
        Check that the two password entries match.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."}
            )
        # You can add more custom validation here if needed
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.
        Handles password hashing.
        """
        # Remove password2 from validated_data as it's not part of the User model
        validated_data.pop("password2")

        # Extract password to use with create_user
        password = validated_data.pop("password")

        # create_user handles normalization of username/email and password hashing
        user = User.objects.create_user(
            **validated_data,  # username, email, first_name, last_name
            password=password,
            is_active=True,  # TODO: Setup email verification, or other means of account activation
        )
        return user


## -- Friend Request Serializers -- ##


class ProfileFriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProfileFriendRequest model.
    Represents a friend request for API output, including profile URLs and Optional messsage.
    """

    # Using SerializerMethodField to generate URLs
    sender_profile_url = serializers.SerializerMethodField()
    receiver_profile_url = serializers.SerializerMethodField()
    accept_url = serializers.SerializerMethodField()
    decline_url = serializers.SerializerMethodField()
    message = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )
    

    message = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )

    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ProfileFriendRequest
        fields = [
            "id",
            "sender_id",
            "receiver_id",
            "message",
            "sender_profile_url",
            "receiver_profile_url",
            "created_at",
            "accept_url",
            "decline_url",
        ]
        read_only_fields = ["id", "created_at"]

    def get_sender_profile_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get("request")
        if request and obj.sender:
            return request.build_absolute_uri(
                reverse("userprofile-detail", kwargs={"pk": obj.sender.id})
            )
        return None

    def get_receiver_profile_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get("request")
        if request and obj.receiver:
            return request.build_absolute_uri(
                reverse("userprofile-detail", kwargs={"pk": obj.receiver.id})
            )
        return None

    def get_accept_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(
                reverse("friend-request-accept", kwargs={"request_pk": obj.id})
            )
        return None

    def get_decline_url(self, obj: ProfileFriendRequest) -> str | None:
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(
                reverse("friend-request-decline", kwargs={"request_pk": obj.id})
            )
        return None


# -- Privacy Settings Serializers -- ##


class UserProfilePrivacySettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfilePrivacySettings model.
    Allows users to view and update their privacy settings.
    """

    user_profile_url = serializers.HyperlinkedRelatedField(
        source="user_profile",
        view_name="userprofile-detail",
        read_only=True,
    )

    class Meta:
        model = UserProfilePrivacySettings
        fields = [
            "id",
            "user_profile_url",
            "search_visibility",
            "profile_visibility",
            "show_full_name",
            "show_email",
            "allow_friend_requests",
            "allow_chat_invites",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id","updated_at"]

    def validate(self, attrs):
        """
        Validate privacy settings for logical consistency.
        """
        search_visibility = attrs.get('search_visibility')
        profile_visibility = attrs.get('profile_visibility')

        # If search visibility is 'nobody', profile should be private or friends_only
        if search_visibility == 'nobody' and profile_visibility == 'public':
            raise serializers.ValidationError(
                "Profile cannot be public if search visibility is set to nobody."
            )

        return attrs


class UserProfilePrivacySettingsReadOnlySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for privacy settings that includes choice labels.
    Used for displaying privacy settings with human-readable labels.
    """

    search_visibility_display = serializers.CharField(
        source='get_search_visibility_display',
        read_only=True
    )
    profile_visibility_display = serializers.CharField(
        source='get_profile_visibility_display',
        read_only=True
    )

    class Meta:
        model = UserProfilePrivacySettings
        fields = [
            "id",
            "search_visibility",
            "search_visibility_display",
            "profile_visibility",
            "profile_visibility_display",
            "show_full_name",
            "show_email",
            "allow_friend_requests",
            "allow_chat_invites",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
