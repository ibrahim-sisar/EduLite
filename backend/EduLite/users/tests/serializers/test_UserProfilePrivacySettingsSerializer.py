# users/tests/serializers/test_UserProfilePrivacySettingsSerializer.py - Tests for UserProfilePrivacySettingsSerializer

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ...models import UserProfile, UserProfilePrivacySettings
from ...serializers import UserProfilePrivacySettingsSerializer


class UserProfilePrivacySettingsSerializerTest(TestCase):
    """Test cases for UserProfilePrivacySettingsSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com"
        )

        # Get profile and privacy settings (created automatically via signals)
        self.profile = self.user.profile
        self.privacy_settings = self.profile.privacy_settings

        # Set some test values
        self.privacy_settings.search_visibility = "friends_of_friends"
        self.privacy_settings.profile_visibility = "friends_only"
        self.privacy_settings.show_full_name = True
        self.privacy_settings.show_email = False
        self.privacy_settings.allow_friend_requests = True
        self.privacy_settings.save()

        # Create request factory for context
        self.factory = APIRequestFactory()

    def get_serializer_context(self, user=None):
        """Get serializer context with request."""
        request = self.factory.get("/")
        if user:
            request.user = user
        return {"request": request}

    # --- Field Presence Tests ---

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = UserProfilePrivacySettingsSerializer(
            instance=self.privacy_settings, context=self.get_serializer_context()
        )
        data = serializer.data

        expected_fields = [
            "search_visibility",
            "profile_visibility",
            "show_full_name",
            "show_email",
            "allow_friend_requests",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    # --- Field Value Tests ---

    def test_field_values_correct(self):
        """Test that field values are correctly serialized."""
        serializer = UserProfilePrivacySettingsSerializer(
            instance=self.privacy_settings, context=self.get_serializer_context()
        )
        data = serializer.data

        # Check field values
        self.assertEqual(data["search_visibility"], "friends_of_friends")
        self.assertEqual(data["profile_visibility"], "friends_only")
        self.assertEqual(data["show_full_name"], True)
        self.assertEqual(data["show_email"], False)
        self.assertEqual(data["allow_friend_requests"], True)

    def test_default_privacy_settings_values(self):
        """Test default values for new privacy settings."""
        # Create new user with default settings (profile/settings created automatically)
        new_user = User.objects.create_user(username="new_user")
        new_profile = new_user.profile
        new_settings = new_profile.privacy_settings

        serializer = UserProfilePrivacySettingsSerializer(
            instance=new_settings, context=self.get_serializer_context()
        )
        data = serializer.data

        # Check default values (based on model defaults)
        self.assertIn("search_visibility", data)
        self.assertIn("profile_visibility", data)
        self.assertIn("show_full_name", data)
        self.assertIn("show_email", data)
        self.assertIn("allow_friend_requests", data)

    # --- Choice Field Tests ---

    def test_visibility_choices_valid(self):
        """Test that visibility choice fields only accept valid values."""
        invalid_data = {
            "search_visibility": "invalid_choice",
            "profile_visibility": "invalid_choice",
        }

        serializer = UserProfilePrivacySettingsSerializer(
            instance=self.privacy_settings,
            data=invalid_data,
            partial=True,
            context=self.get_serializer_context(),
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("search_visibility", serializer.errors)
        self.assertIn("profile_visibility", serializer.errors)

    def test_boolean_fields_validation(self):
        """Test boolean field validation."""
        # Test with various boolean values
        test_data = {
            "show_full_name": False,
            "show_email": True,
            "allow_friend_requests": False,
        }

        serializer = UserProfilePrivacySettingsSerializer(
            instance=self.privacy_settings,
            data=test_data,
            partial=True,
            context=self.get_serializer_context(),
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["show_full_name"], False)
        self.assertEqual(serializer.validated_data["show_email"], True)
        self.assertEqual(serializer.validated_data["allow_friend_requests"], False)

    # --- Update Tests ---

    def test_partial_update(self):
        """Test partial update of privacy settings."""
        update_data = {"search_visibility": "nobody", "allow_friend_requests": False}

        serializer = UserProfilePrivacySettingsSerializer(
            instance=self.privacy_settings,
            data=update_data,
            partial=True,
            context=self.get_serializer_context(),
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Verify changes
        self.privacy_settings.refresh_from_db()
        self.assertEqual(self.privacy_settings.search_visibility, "nobody")
        self.assertEqual(self.privacy_settings.allow_friend_requests, False)
        # Other fields should remain unchanged
        self.assertEqual(self.privacy_settings.profile_visibility, "friends_only")

    def test_full_update(self):
        """Test full update of privacy settings."""
        update_data = {
            "search_visibility": "everyone",
            "profile_visibility": "public",
            "show_full_name": False,
            "show_email": True,
            "allow_friend_requests": True,
        }

        serializer = UserProfilePrivacySettingsSerializer(
            instance=self.privacy_settings,
            data=update_data,
            context=self.get_serializer_context(),
        )

        self.assertTrue(serializer.is_valid())
        serializer.save()

        # Verify all changes
        self.privacy_settings.refresh_from_db()
        self.assertEqual(self.privacy_settings.search_visibility, "everyone")
        self.assertEqual(self.privacy_settings.profile_visibility, "public")
        self.assertEqual(self.privacy_settings.show_full_name, False)
        self.assertEqual(self.privacy_settings.show_email, True)
        self.assertEqual(self.privacy_settings.allow_friend_requests, True)
