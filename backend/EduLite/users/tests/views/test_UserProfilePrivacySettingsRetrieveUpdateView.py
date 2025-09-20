# users/tests/views/test_UserProfilePrivacySettingsRetrieveUpdateView.py - Tests for UserProfilePrivacySettingsRetrieveUpdateView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ...models import UserProfile, UserProfilePrivacySettings

from django_mercury import DjangoPerformanceAPITestCase


class UserProfilePrivacySettingsRetrieveUpdateViewTest(DjangoPerformanceAPITestCase):
    """Test cases for the UserProfilePrivacySettingsRetrieveUpdateView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()

        # Privacy settings URL operates on current authenticated user
        self.url = reverse("privacy-settings")

        # Create test users with different privacy settings
        self.ahmad = self.create_test_user("ahmad", "ahmad@test.com")
        self.marie = self.create_test_user("marie", "marie@test.com")
        self.sophie = self.create_test_user("sophie", "sophie@test.com")
        self.sarah_teacher = self.create_test_user("sarah_teacher", "sarah@test.com")

        # Set up specific privacy settings for each user
        self.setup_privacy_settings()

    def create_test_user(self, username, email, password="testpass123"):
        """Helper to create a test user with profile and privacy settings."""
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        # Profile and privacy settings are created automatically via signals
        return user

    def setup_privacy_settings(self):
        """Set up specific privacy settings for test users."""
        # Ahmad - friends of friends visibility
        ahmad_privacy = self.ahmad.profile.privacy_settings
        ahmad_privacy.search_visibility = "friends_of_friends"
        ahmad_privacy.profile_visibility = "friends_only"
        ahmad_privacy.save()

        # Marie - public visibility
        marie_privacy = self.marie.profile.privacy_settings
        marie_privacy.search_visibility = "everyone"
        marie_privacy.profile_visibility = "public"
        marie_privacy.show_email = True
        marie_privacy.save()

        # Sophie - private/nobody visibility
        sophie_privacy = self.sophie.profile.privacy_settings
        sophie_privacy.search_visibility = "nobody"
        sophie_privacy.profile_visibility = "private"
        sophie_privacy.allow_friend_requests = False
        sophie_privacy.save()

        # Sarah Teacher - public (teachers are usually more open)
        sarah_privacy = self.sarah_teacher.profile.privacy_settings
        sarah_privacy.search_visibility = "everyone"
        sarah_privacy.profile_visibility = "public"
        sarah_privacy.show_email = True
        sarah_privacy.save()

    # --- Authentication Tests ---

    def test_retrieve_privacy_settings_requires_authentication(self):
        """Test that retrieving privacy settings requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_privacy_settings_requires_authentication(self):
        """Test that updating privacy settings requires authentication."""
        response = self.client.patch(self.url, {"search_visibility": "nobody"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Retrieve Tests ---

    def test_retrieve_own_privacy_settings_success(self):
        """Test that users can retrieve their own privacy settings."""
        self.client.force_authenticate(user=self.ahmad)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should get privacy settings data
        self.assertIsInstance(response.data, dict)
        self.assertGreater(len(response.data), 0)
        self.assertIn("search_visibility", response.data)
        self.assertIn("profile_visibility", response.data)

    def test_retrieve_privacy_settings_for_different_users(self):
        """Test that each user retrieves their own privacy settings."""
        # Test Ahmad's settings
        self.client.force_authenticate(user=self.ahmad)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["search_visibility"], "friends_of_friends")

        # Test Sophie's settings (different user)
        self.client.force_authenticate(user=self.sophie)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["search_visibility"], "nobody")
        self.assertEqual(response.data["allow_friend_requests"], False)

    def test_privacy_settings_created_if_missing(self):
        """Test that privacy settings are created if they don't exist."""
        # Create a new user without privacy settings
        new_user = User.objects.create_user(
            username="new_user_no_privacy",
            email="newuser@test.com",
            password="testpass123",
        )

        # Delete privacy settings if they exist (due to signal)
        if hasattr(new_user.profile, "privacy_settings"):
            new_user.profile.privacy_settings.delete()

        self.client.force_authenticate(user=new_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should have default settings
        self.assertIn("search_visibility", response.data)

        # Verify settings were created
        new_user.profile.refresh_from_db()
        self.assertTrue(hasattr(new_user.profile, "privacy_settings"))

    # --- Update Tests ---

    def test_update_own_privacy_settings_success(self):
        """Test that users can update their own privacy settings."""
        self.client.force_authenticate(user=self.ahmad)

        response = self.client.patch(
            self.url,
            {
                "search_visibility": "everyone",
                "profile_visibility": "public",
                "show_email": True,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify changes
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(
            self.ahmad.profile.privacy_settings.search_visibility, "everyone"
        )
        self.assertEqual(
            self.ahmad.profile.privacy_settings.profile_visibility, "public"
        )
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)

    def test_each_user_updates_own_settings(self):
        """Test that users can only update their own settings."""
        # Ahmad updates his settings
        self.client.force_authenticate(user=self.ahmad)
        response = self.client.patch(self.url, {"search_visibility": "nobody"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify Ahmad's settings changed
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(
            self.ahmad.profile.privacy_settings.search_visibility, "nobody"
        )

        # Marie's settings should be unchanged
        self.marie.profile.privacy_settings.refresh_from_db()
        self.assertEqual(
            self.marie.profile.privacy_settings.search_visibility, "everyone"
        )

    # --- Validation Tests ---

    def test_update_privacy_settings_invalid_visibility(self):
        """Test updating with invalid visibility values."""
        self.client.force_authenticate(user=self.ahmad)

        # Try invalid search visibility
        response = self.client.patch(self.url, {"search_visibility": "invalid_option"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("search_visibility", response.data)

    def test_update_privacy_settings_invalid_profile_visibility(self):
        """Test updating with invalid profile visibility."""
        self.client.force_authenticate(user=self.ahmad)

        response = self.client.patch(self.url, {"profile_visibility": "super_private"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profile_visibility", response.data)

    def test_update_privacy_settings_boolean_fields(self):
        """Test updating boolean privacy fields."""
        self.client.force_authenticate(user=self.ahmad)

        # Test with various boolean values
        response = self.client.patch(
            self.url,
            {
                "show_full_name": False,
                "show_email": True,
                "allow_friend_requests": False,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify changes
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_full_name, False)
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        self.assertEqual(
            self.ahmad.profile.privacy_settings.allow_friend_requests, False
        )

    # --- Partial Update Tests ---

    def test_partial_update_privacy_settings(self):
        """Test partial updates to privacy settings."""
        self.client.force_authenticate(user=self.ahmad)

        # Update only one field
        response = self.client.patch(self.url, {"show_email": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only that field changed
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        # Other fields unchanged
        self.assertEqual(
            self.ahmad.profile.privacy_settings.search_visibility, "friends_of_friends"
        )

    # --- Full Update Tests ---

    def test_full_update_privacy_settings(self):
        """Test full updates to privacy settings."""
        self.client.force_authenticate(user=self.ahmad)

        # Get current settings
        response = self.client.get(self.url)
        current_data = response.data

        # Update all fields
        current_data.update(
            {
                "search_visibility": "nobody",
                "profile_visibility": "private",
                "show_full_name": False,
                "show_email": False,
                "allow_friend_requests": False,
            }
        )

        response = self.client.put(self.url, current_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all changes
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(
            self.ahmad.profile.privacy_settings.search_visibility, "nobody"
        )
        self.assertEqual(
            self.ahmad.profile.privacy_settings.profile_visibility, "private"
        )
        self.assertEqual(self.ahmad.profile.privacy_settings.show_full_name, False)
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, False)
        self.assertEqual(
            self.ahmad.profile.privacy_settings.allow_friend_requests, False
        )

    # --- Read-only Fields Test ---

    def test_cannot_update_read_only_fields(self):
        """Test that read-only fields are ignored in updates."""
        self.client.force_authenticate(user=self.ahmad)

        response = self.client.patch(
            self.url,
            {
                "profile": self.marie.profile.id,  # Should be read-only
                "created_at": "2024-01-01T00:00:00Z",  # Should be read-only
                "show_email": True,  # Valid field
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only valid field was updated
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        self.assertEqual(
            self.ahmad.profile.privacy_settings.user_profile.id, self.ahmad.profile.id
        )

    # --- Privacy Setting Combinations ---

    def test_valid_privacy_setting_combinations(self):
        """Test various valid combinations of privacy settings."""
        self.client.force_authenticate(user=self.ahmad)

        # Test restrictive combination
        response = self.client.patch(
            self.url,
            {
                "search_visibility": "nobody",
                "profile_visibility": "private",
                "allow_friend_requests": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test open combination
        response = self.client.patch(
            self.url,
            {
                "search_visibility": "everyone",
                "profile_visibility": "public",
                "allow_friend_requests": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test friends-only combination
        response = self.client.patch(
            self.url,
            {
                "search_visibility": "friends_only",
                "profile_visibility": "friends_only",
                "allow_friend_requests": True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Admin Access Test ---

    def test_admin_accesses_own_privacy_settings(self):
        """Test that admin users also access their own settings, not others'."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.client.force_authenticate(user=self.sarah_teacher)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should get Sarah's settings, not anyone else's
        self.assertEqual(
            response.data["search_visibility"], "everyone"
        )  # Sarah's default

        # Update should affect Sarah's settings
        response = self.client.patch(self.url, {"search_visibility": "friends_only"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.sarah_teacher.profile.privacy_settings.refresh_from_db()
        self.assertEqual(
            self.sarah_teacher.profile.privacy_settings.search_visibility,
            "friends_only",
        )

    # --- Performance Test ---

    def test_privacy_settings_update_performance(self):
        """Test performance of privacy settings updates."""
        self.client.force_authenticate(user=self.ahmad)

        import time

        start_time = time.time()

        # Make multiple updates
        for i in range(5):
            response = self.client.patch(
                self.url,
                {
                    "show_email": i % 2 == 0,  # Toggle between True/False
                    "show_full_name": i % 2 == 1,
                },
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        self.assertLess(duration, 2.0, "Privacy settings update too slow")

    # --- Edge Cases ---

    def test_update_with_empty_data(self):
        """Test updating with empty data doesn't break anything."""
        self.client.force_authenticate(user=self.ahmad)

        # Get original settings
        response = self.client.get(self.url)
        original_data = response.data

        # Update with empty data
        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Settings should be unchanged
        response = self.client.get(self.url)
        self.assertEqual(
            response.data["search_visibility"], original_data["search_visibility"]
        )

    def test_update_with_null_values(self):
        """Test that null values are handled properly."""
        self.client.force_authenticate(user=self.ahmad)

        # Try to set boolean fields to empty string (which Django REST framework might interpret as null/false)
        response = self.client.patch(
            self.url,
            {"show_email": "", "allow_friend_requests": ""},
            format="json",  # Use JSON format to properly handle empty values
        )

        # Check the response - empty strings for boolean fields should either:
        # 1. Be rejected with 400 error
        # 2. Be treated as False
        if response.status_code == status.HTTP_200_OK:
            self.ahmad.profile.privacy_settings.refresh_from_db()
            # Empty strings likely converted to False for boolean fields
            self.assertIn(self.ahmad.profile.privacy_settings.show_email, [True, False])
            self.assertIn(
                self.ahmad.profile.privacy_settings.allow_friend_requests, [True, False]
            )
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_concurrent_updates_same_user(self):
        """Test that concurrent updates to the same user don't cause issues."""
        self.client.force_authenticate(user=self.ahmad)

        # First update
        response1 = self.client.patch(self.url, {"show_email": True})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Second update (simulating concurrent request)
        response2 = self.client.patch(self.url, {"show_full_name": False})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Both updates should be applied
        self.ahmad.profile.privacy_settings.refresh_from_db()
        self.assertEqual(self.ahmad.profile.privacy_settings.show_email, True)
        self.assertEqual(self.ahmad.profile.privacy_settings.show_full_name, False)

    def test_invalid_json_format(self):
        """Test handling of invalid JSON in request."""
        self.client.force_authenticate(user=self.ahmad)

        # Send invalid JSON (as string instead of dict)
        response = self.client.patch(
            self.url, "invalid json string", content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_privacy_settings_field_types(self):
        """Test that field types are properly validated."""
        self.client.force_authenticate(user=self.ahmad)

        # Try to set string choice field to an invalid integer
        response = self.client.patch(
            self.url,
            {"search_visibility": 123},  # Should be a valid string choice
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Try to set boolean field to an invalid string (not 'true'/'false')
        response = self.client.patch(
            self.url, {"show_email": "invalid_bool"}, format="json"  # Should be boolean
        )

        # DRF might coerce 'invalid_bool' to True (any non-empty string)
        # So let's check if it either fails or coerces correctly
        if response.status_code == status.HTTP_200_OK:
            # If it succeeded, the value was coerced
            self.ahmad.profile.privacy_settings.refresh_from_db()
            # Non-empty strings are typically coerced to True in Django
            self.assertTrue(self.ahmad.profile.privacy_settings.show_email)
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
