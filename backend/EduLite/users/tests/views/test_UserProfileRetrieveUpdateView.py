# users/tests/views/test_UserProfileRetrieveUpdateView.py - Tests for UserProfileRetrieveUpdateView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase


class UserProfileRetrieveUpdateViewTest(UsersAppTestCase):
    """Test cases for the UserProfileRetrieveUpdateView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        # URL pattern should be like /api/users/{user_id}/profile/
        self.get_url = lambda user_id: reverse(
            "userprofile-detail", kwargs={"pk": user_id}
        )

    # --- Authentication Tests ---

    def test_retrieve_profile_requires_authentication(self):
        """Test that retrieving a profile requires authentication."""
        url = self.get_url(self.ahmad.id)
        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_requires_authentication(self):
        """Test that updating a profile requires authentication."""
        url = self.get_url(self.ahmad.id)
        response = self.client.patch(url, {"bio": "Updated bio"})
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- Retrieve Tests ---

    def test_retrieve_own_profile_success(self):
        """Test that users can retrieve their own profile."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.ahmad.id)

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should get profile data (specific fields tested in serializer tests)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.data["user"], self.ahmad.id)

    def test_retrieve_other_user_profile_public(self):
        """Test retrieving another user's profile with public visibility."""
        # Marie has public profile visibility
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.marie.id)

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should see marie's profile
        self.assertEqual(response.data["user"], self.marie.id)

    def test_retrieve_other_user_profile_friends_only(self):
        """Test retrieving profile with friends_only visibility."""
        # Ahmad has friends_only profile visibility
        # Ahmad and Marie are friends
        self.authenticate_as(self.marie)
        url = self.get_url(self.ahmad.id)

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

    def test_retrieve_profile_blocked_by_privacy(self):
        """Test that private profiles return limited data for non-friends."""
        # Sophie has private profile visibility
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.sophie.id)

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should get limited data (privacy logic tested in serializer tests)
        self.assertIsInstance(response.data, dict)

    def test_retrieve_nonexistent_profile(self):
        """Test retrieving profile for non-existent user."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(99999)

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_admin_can_retrieve_any_profile(self):
        """Test that admin users can retrieve any profile."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Should be able to see Sophie's private profile
        url = self.get_url(self.sophie.id)
        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

    # --- Update Tests ---

    def test_update_own_profile_success(self):
        """Test that users can update their own profile."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.ahmad.id)

        new_bio = "Updated bio - Still learning despite challenges in Gaza."
        response = self.client.patch(url, {"bio": new_bio, "occupation": "developer"})

        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify changes
        self.ahmad.profile.refresh_from_db()
        self.assertEqual(self.ahmad.profile.bio, new_bio)
        self.assertEqual(self.ahmad.profile.occupation, "developer")

    def test_update_other_user_profile_forbidden(self):
        """Test that users cannot update other users' profiles."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.marie.id)

        response = self.client.patch(url, {"bio": "Hacked bio"})
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify no changes
        self.marie.profile.refresh_from_db()
        self.assertNotEqual(self.marie.profile.bio, "Hacked bio")

    def test_admin_can_update_any_profile(self):
        """Test that admin users can update any profile."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)
        url = self.get_url(self.ahmad.id)

        response = self.client.patch(
            url, {"bio": "Updated by admin for safety reasons"}
        )

        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify changes
        self.ahmad.profile.refresh_from_db()
        self.assertEqual(self.ahmad.profile.bio, "Updated by admin for safety reasons")

    def test_update_profile_validation(self):
        """Test profile update validation."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.ahmad.id)

        # Try to set invalid country code
        response = self.client.patch(url, {"country": "INVALID"})
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_partial(self):
        """Test partial profile updates (PATCH)."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.ahmad.id)

        # Update only bio
        response = self.client.patch(url, {"bio": "Just updating bio"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Other fields should remain unchanged
        self.ahmad.profile.refresh_from_db()
        self.assertEqual(self.ahmad.profile.bio, "Just updating bio")
        self.assertEqual(self.ahmad.profile.country, "PS")  # Unchanged

    def test_update_profile_full(self):
        """Test full profile updates (PUT)."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.ahmad.id)

        # Get current profile data
        response = self.client.get(url)
        current_data = response.data

        # Clean None values for multipart encoding
        current_data = {k: v if v is not None else "" for k, v in current_data.items()}

        # Update with full data
        current_data["bio"] = "Complete profile update"
        current_data["website_url"] = "https://example.com"

        response = self.client.put(url, current_data)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify changes
        self.ahmad.profile.refresh_from_db()
        self.assertEqual(self.ahmad.profile.bio, "Complete profile update")
        self.assertEqual(self.ahmad.profile.website_url, "https://example.com")

    def test_update_read_only_fields_ignored(self):
        """Test that read-only fields are ignored in updates."""
        self.authenticate_as(self.ahmad)
        url = self.get_url(self.ahmad.id)

        # Try to update read-only fields
        response = self.client.patch(
            url,
            {
                "user": self.marie.id,  # Should be read-only
                "created_at": "2024-01-01T00:00:00Z",  # Should be read-only
                "bio": "Valid update",
            },
        )

        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify only bio was updated
        self.ahmad.profile.refresh_from_db()
        self.assertEqual(self.ahmad.profile.bio, "Valid update")
        self.assertEqual(self.ahmad.profile.user.id, self.ahmad.id)  # Unchanged

    # --- Privacy Integration Tests ---

    def test_profile_visibility_respects_privacy_settings(self):
        """Test that profile visibility respects privacy settings."""
        # Create a new user with specific privacy settings
        test_user = self.create_test_user(username="privacy_test")
        test_user.profile.bio = "Test bio"
        test_user.profile.save()

        # Set to nobody visibility (assuming this means 'private')
        test_user.profile.privacy_settings.profile_visibility = "private"
        test_user.profile.privacy_settings.save()

        # Non-admin should get limited data
        self.authenticate_as(self.ahmad)
        url = self.get_url(test_user.id)
        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should get limited data (specific fields tested in serializer tests)
        self.assertIsInstance(response.data, dict)

    # --- Field Privacy Tests ---

    def test_sensitive_fields_hidden_based_on_privacy(self):
        """Test that sensitive fields are hidden based on privacy settings."""
        # Joy has friends_only visibility
        # Elena is Joy's friend
        self.authenticate_as(self.elena)
        url = self.get_url(self.joy.id)

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should get data based on friendship (privacy logic tested in serializer tests)
        self.assertIsInstance(response.data, dict)

    # --- Performance Test ---

    def test_profile_retrieve_performance(self):
        """Test that profile retrieval is performant."""
        self.authenticate_as(self.ahmad)

        import time

        start_time = time.time()

        # Retrieve multiple profiles
        for user in [self.marie, self.joy, self.elena, self.fatima]:
            url = self.get_url(user.id)
            response = self.client.get(url)
            self.assert_response_success(response)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time
        self.assertLess(duration, 2.0, "Profile retrieval too slow")
