from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models
from django.conf import settings
from typing import Optional, TYPE_CHECKING

from rest_framework import serializers

from .models import (
    UserProfile,
    ProfileFriendRequest,
    UserProfilePrivacySettings,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.signing import TimestampSigner
import json
import base64


User = get_user_model()


# -- Profile Serializers -- ##


class ProfileSerializer(
    serializers.HyperlinkedModelSerializer
):  # Or HyperlinkedModelSerializer if you prefer
    """
    Serializer for the UserProfile model.
    Privacy-aware serializer that respects UserProfilePrivacySettings.
    """

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_url = serializers.HyperlinkedRelatedField(
        source="user",
        view_name="user-detail",
        read_only=True,
    )
    friends = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        default=[],
        help_text="List of user IDs who are friends",
    )

    class Meta:
        model = UserProfile
        fields = [
            "url",  # URL for the UserProfile instance itself
            "user",  # User ID
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

    def _get_requesting_user(self) -> Optional["AbstractUser"]:
        """Get the requesting user from context."""
        request = self.context.get("request")

        # Production: Get authenticated user from request
        if (
            request
            and hasattr(request, "user")
            and hasattr(request.user, "is_authenticated")
            and request.user.is_authenticated
        ):
            return request.user

        # Test context: Allow passing user directly (only for tests)
        test_user = self.context.get("test_user")
        if test_user and hasattr(test_user, "pk"):
            return test_user

        return None

    def _can_view_full_profile(
        self, obj: UserProfile, requesting_user: Optional["AbstractUser"]
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
            privacy_settings = getattr(obj, "privacy_settings", None)
            if privacy_settings:
                return privacy_settings.can_profile_be_viewed_by_user(requesting_user)
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
            limited_fields = ["url", "user_url"]
            representation = {
                key: value
                for key, value in representation.items()
                if key in limited_fields
            }

        return representation


# -- User/Group Hyperlinked Serializers -- ##


class UserSearchSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for user search results.
    Optimized to minimize database queries by avoiding hyperlinked fields.
    """

    full_name = serializers.SerializerMethodField()
    profile_id = serializers.IntegerField(source="profile.id", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "profile_id",
        ]

    def get_full_name(self, obj):
        """Get full name efficiently."""
        first = obj.first_name
        last = obj.last_name
        if first and last:
            return f"{first} {last}"
        elif first:
            return first
        elif last:
            return last
        return ""

    def _get_requesting_user(self):
        """Get the requesting user from context."""
        request = self.context.get("request")
        if (
            request
            and hasattr(request, "user")
            and hasattr(request.user, "is_authenticated")
            and request.user.is_authenticated
        ):
            return request.user
        return None

    def _get_privacy_settings(self, obj):
        """
        Get privacy settings for the user, with caching to avoid multiple DB hits.
        """
        cache_key = f"_privacy_settings_{id(obj)}"
        if hasattr(self, cache_key):
            return getattr(self, cache_key)

        privacy_settings = None
        try:
            if hasattr(obj, "profile") and hasattr(obj.profile, "privacy_settings"):
                privacy_settings = obj.profile.privacy_settings
        except (AttributeError, UserProfilePrivacySettings.DoesNotExist):
            pass

        setattr(self, cache_key, privacy_settings)
        return privacy_settings

    def to_representation(self, instance):
        """
        Override to apply privacy filtering efficiently.
        """
        representation = super().to_representation(instance)
        requesting_user = self._get_requesting_user()

        # Apply privacy filtering
        if requesting_user and instance.id == requesting_user.id:
            # User can see all their own data
            return representation

        if requesting_user and (
            requesting_user.is_superuser or requesting_user.is_staff
        ):
            # Admin can see all data
            return representation

        # Check privacy settings
        privacy_settings = self._get_privacy_settings(instance)

        if not privacy_settings:
            # Default privacy: hide email
            representation.pop("email", None)
        else:
            if not privacy_settings.show_email:
                representation.pop("email", None)

            if not privacy_settings.show_full_name:
                representation.pop("first_name", None)
                representation.pop("last_name", None)
                representation.pop("full_name", None)

        return representation


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
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
        default=[],
        help_text="List of group IDs the user belongs to",
    )

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

    def _get_requesting_user(self):
        """Get the requesting user from context."""
        request = self.context.get("request")

        # Production: Get authenticated user from request
        if (
            request
            and hasattr(request, "user")
            and hasattr(request.user, "is_authenticated")
            and request.user.is_authenticated
        ):
            return request.user

        # Test context: Allow passing user directly (only for tests)
        test_user = self.context.get("test_user")  # Doesn't exist without test
        if test_user and hasattr(test_user, "pk"):
            return test_user

        return None

    def _get_privacy_settings(self, obj):
        """
        Get privacy settings for the user, with caching to avoid multiple DB hits.
        Uses instance-level caching to prevent repeated access within the same serialization.
        """
        # Create a cache key specific to this serializer instance and object
        cache_key = f"_privacy_settings_{id(obj)}"

        # Check if we've already fetched privacy settings for this object
        if hasattr(self, cache_key):
            return getattr(self, cache_key)

        # Fetch privacy settings
        privacy_settings = None
        try:
            if hasattr(obj, "profile") and hasattr(obj.profile, "privacy_settings"):
                privacy_settings = obj.profile.privacy_settings
        except (AttributeError, UserProfilePrivacySettings.DoesNotExist):
            pass

        # Cache the result on this serializer instance
        setattr(self, cache_key, privacy_settings)
        return privacy_settings

    def _should_show_email(
        self, obj, requesting_user: Optional["AbstractUser"]
    ) -> bool:
        """
        Determine if email should be shown to the requesting user.
        """
        # User can always see their own email - use pk comparison
        if requesting_user and obj.pk == requesting_user.pk:
            return True

        # Admin users can see all emails
        if requesting_user and (
            requesting_user.is_superuser or requesting_user.is_staff
        ):
            return True

        # Check privacy settings using cached method
        privacy_settings = self._get_privacy_settings(obj)
        if privacy_settings:
            return privacy_settings.show_email

        # Default to hiding email if no privacy settings exist
        return False

    def _should_show_full_name(
        self, obj, requesting_user: Optional["AbstractUser"]
    ) -> bool:
        """
        Determine if full name should be shown to the requesting user.
        """
        # User can always see their own name - fix the comparison
        if requesting_user and obj.id == requesting_user.id:
            return True

        # Admin users can see all names
        if requesting_user and (
            requesting_user.is_superuser or requesting_user.is_staff
        ):
            return True

        # Check privacy settings using cached method
        privacy_settings = self._get_privacy_settings(obj)
        if privacy_settings:
            return privacy_settings.show_full_name

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
            representation.pop("email", None)

        if not self._should_show_full_name(instance, requesting_user):
            representation.pop("first_name", None)
            representation.pop("last_name", None)
            representation.pop("full_name", None)

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

        # Cache blocked domains to avoid repeated getattr calls
        if not hasattr(self, "_blocked_domains"):
            blocked_domains = getattr(
                settings, "BLOCKED_EMAIL_DOMAINS", ["example.com", "test.com"]
            )
            # Pre-process to lowercase for faster comparison
            self._blocked_domains = [d.lower() for d in blocked_domains]

        if domain_part.lower() in self._blocked_domains:
            raise serializers.ValidationError(
                "Registration from this email domain is not allowed."
            )

        return value  # Domain validation passes, uniqueness checked in validate()

    def validate_username(self, value):
        """
        Check that the username format is valid.
        Uniqueness will be checked in validate() method.
        """
        return value

    def validate(self, attrs):
        """
        Check that the two password entries match and perform uniqueness checks.
        Combined validation reduces database queries from 2 to 1.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Password fields didn't match."}
            )

        # Perform combined uniqueness check using a single query
        username = attrs.get("username")
        email = attrs.get("email")

        if username and email:
            # Use Q objects for efficient OR query
            existing_users = User.objects.filter(
                models.Q(username__iexact=username) | models.Q(email__iexact=email)
            ).values("username", "email")

            errors = {}
            for user in existing_users:
                if user["username"].lower() == username.lower():
                    errors["username"] = "A user with that username already exists."
                if user["email"].lower() == email.lower():
                    errors["email"] = "A user with this email address already exists."

            if errors:
                raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        """
        Handles user registration based on EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP setting.

        If verification required:
        - Sends verification email with signed token
        - Does NOT create user yet (happens on email verification)

        If verification not required:
        - Creates user immediately
        - Still sends verification email for optional verification
        """
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Check if email verification is required
        require_verification = getattr(
            settings, "USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP", False
        )

        # Prepare email verification token
        signer = TimestampSigner()
        payload = {
            "email": validated_data["email"],
            "username": validated_data["username"],
            "password": password,
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
        }

        json_payload = json.dumps(payload)
        b64_payload = base64.urlsafe_b64encode(json_payload.encode()).decode()
        signed_token = signer.sign(b64_payload)

        verification_link = (
            f"{settings.FRONTEND_URL}/verify-email/?token={signed_token}"
        )

        # Send verification email
        subject = render_to_string("email/account_verification_subject.txt").strip()
        text_content = render_to_string(
            "email/account_verification_email.txt",
            {
                "username": payload["username"],
                "activation_link": verification_link,
            },
        )
        html_content = render_to_string(
            "email/account_verification_email.html",
            {
                "username": payload["username"],
                "activation_link": verification_link,
            },
        )

        email = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [payload["email"]]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        if require_verification:
            # Don't create user yet - wait for email verification
            return {"message": "Verification email sent."}
        else:
            # Create user immediately but still send verification email
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=password,
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
            )

            # Create UserProfile with defaults
            from .models import UserProfile

            UserProfile.objects.get_or_create(user=user)

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
    # Include nested sender and receiver user info
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    message = serializers.CharField(required=False, allow_blank=True, max_length=500)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ProfileFriendRequest
        fields = [
            "id",
            "sender_id",
            "receiver_id",
            "sender",
            "receiver",
            "message",
            "sender_profile_url",
            "receiver_profile_url",
            "created_at",
            "accept_url",
            "decline_url",
        ]
        read_only_fields = ["id", "created_at"]

    def get_sender(self, obj: ProfileFriendRequest) -> dict:
        """Return basic sender user info."""
        if obj.sender and obj.sender.user:
            return {
                "id": obj.sender.user.id,
                "username": obj.sender.user.username,
                "first_name": obj.sender.user.first_name,
                "last_name": obj.sender.user.last_name,
            }
        return None

    def get_receiver(self, obj: ProfileFriendRequest) -> dict:
        """Return basic receiver user info."""
        if obj.receiver and obj.receiver.user:
            return {
                "id": obj.receiver.user.id,
                "username": obj.receiver.user.username,
                "first_name": obj.receiver.user.first_name,
                "last_name": obj.receiver.user.last_name,
            }
        return None

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
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Validate privacy settings for logical consistency.
        """
        search_visibility = attrs.get("search_visibility")
        profile_visibility = attrs.get("profile_visibility")

        # If search visibility is 'nobody', profile should be private or friends_only
        if search_visibility == "nobody" and profile_visibility == "public":
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
        source="get_search_visibility_display", read_only=True
    )
    profile_visibility_display = serializers.CharField(
        source="get_profile_visibility_display", read_only=True
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
