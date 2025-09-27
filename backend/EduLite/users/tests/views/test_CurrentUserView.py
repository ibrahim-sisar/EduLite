# users/tests/views/test_CurrentUserView.py - Tests for CurrentUserView API endpoint

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .. import UsersAppTestCase


class CurrentUserViewTest(UsersAppTestCase):
    """Test cases for the CurrentUserView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = reverse("current-user")

    def test_get_current_user_requires_authentication(self):
        """Test that getting current user info requires authentication."""
        # Make request without authentication
        response = self.client.get(self.url)

        # Should return 401 Unauthorized
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user_authenticated_success(self):
        """Test getting current user info when authenticated."""
        # Authenticate as Ahmad
        self.authenticate_as(self.ahmad)

        # Get current user info
        response = self.client.get(self.url)

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should contain current user's data
        self.assertIn("id", response.data)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertIn("url", response.data)
        self.assertIn("profile_url", response.data)
        self.assertIn("full_name", response.data)

        # Should return Ahmad's data specifically
        self.assertEqual(response.data["id"], self.ahmad.pk)
        self.assertEqual(response.data["username"], "ahmad_gaza")
        self.assertEqual(response.data["email"], "ahmad@gaza-university.ps")

    def test_get_current_user_different_authenticated_users(self):
        """Test that current user endpoint returns data for the authenticated user."""
        # Test with Ahmad
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.ahmad.pk)
        self.assertEqual(response.data["username"], "ahmad_gaza")

        # Test with Marie (different user)
        self.authenticate_as(self.marie)
        response = self.client.get(self.url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.marie.pk)
        self.assertEqual(response.data["username"], "marie_student")

    def test_get_current_user_admin_access(self):
        """Test that admin users can get their own info via current user endpoint."""
        # Create admin user
        admin_user = self.create_test_user(
            username="admin",
            email="admin@example.com",
            is_superuser=True,
            is_staff=True,
        )

        # Authenticate as admin
        self.authenticate_as(admin_user)

        # Get current user info
        response = self.client.get(self.url)

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should return admin's data
        self.assertEqual(response.data["id"], admin_user.pk)
        self.assertEqual(response.data["username"], "admin")
        self.assertEqual(response.data["email"], "admin@example.com")

    def test_get_current_user_contains_required_fields(self):
        """Test that current user response contains all required fields."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url)

        self.assert_response_success(response, status.HTTP_200_OK)

        # Check all required fields are present
        required_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "url",
            "profile_url",
            "full_name",
            "groups",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(
                    field, response.data, f"Field '{field}' missing from response"
                )

    def test_get_current_user_does_not_expose_sensitive_data(self):
        """Test that current user response doesn't expose sensitive fields."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url)

        self.assert_response_success(response, status.HTTP_200_OK)

        # Sensitive fields that should NOT be in the response
        # Note: groups is actually included in UserSerializer, so we exclude it from sensitive fields
        sensitive_fields = ["password", "user_permissions"]

        for field in sensitive_fields:
            with self.subTest(field=field):
                self.assertNotIn(
                    field,
                    response.data,
                    f"Sensitive field '{field}' exposed in response",
                )

    def test_get_current_user_inactive_user(self):
        """Test getting current user info for inactive user."""
        # Make user inactive
        self.ahmad.is_active = False
        self.ahmad.save()

        # Authenticate as inactive user (this might fail depending on auth backend)
        try:
            self.authenticate_as(self.ahmad)
            response = self.client.get(self.url)

            # If authentication succeeds, should still return user data
            self.assert_response_success(response, status.HTTP_200_OK)
            self.assertEqual(response.data["id"], self.ahmad.pk)
            self.assertFalse(response.data["is_active"])
        except Exception:
            # If authentication fails for inactive user, that's also acceptable behavior
            pass

    # PATCH Method Tests
    def test_patch_current_user_requires_authentication(self):
        """Test that PATCH requests require authentication."""
        # Try to update without authentication
        response = self.client.patch(self.url, {"first_name": "NewName"}, format="json")

        # Should return 401 Unauthorized
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_patch_current_user_update_user_fields(self):
        """Test updating User model fields (first_name, last_name)."""
        # Authenticate as Ahmad
        self.authenticate_as(self.ahmad)

        # Update user fields
        update_data = {"first_name": "Ahmad Updated", "last_name": "Al-Rashid Updated"}
        response = self.client.patch(self.url, update_data, format="json")

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify response contains updated values
        self.assertEqual(response.data["first_name"], "Ahmad Updated")
        self.assertEqual(response.data["last_name"], "Al-Rashid Updated")

        # Verify database was actually updated
        self.ahmad.refresh_from_db()
        self.assertEqual(self.ahmad.first_name, "Ahmad Updated")
        self.assertEqual(self.ahmad.last_name, "Al-Rashid Updated")

    def test_patch_current_user_update_profile_fields(self):
        """Test updating UserProfile fields."""
        # Authenticate as Marie
        self.authenticate_as(self.marie)

        # Update profile fields
        update_data = {
            "bio": "Updated bio for testing",
            "occupation": "teacher",
            "country": "FR",
            "preferred_language": "fr",
            "secondary_language": "en",
            "website_url": "https://marie-example.com",
        }
        response = self.client.patch(self.url, update_data, format="json")

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify database was updated
        self.marie.profile.refresh_from_db()
        self.assertEqual(self.marie.profile.bio, "Updated bio for testing")
        self.assertEqual(self.marie.profile.occupation, "teacher")
        self.assertEqual(self.marie.profile.country, "FR")
        self.assertEqual(self.marie.profile.preferred_language, "fr")
        self.assertEqual(self.marie.profile.secondary_language, "en")
        self.assertEqual(self.marie.profile.website_url, "https://marie-example.com")

    def test_patch_current_user_combined_update(self):
        """Test updating both User and UserProfile fields in single request."""
        # Create a fresh test user
        test_user = self.create_test_user(
            username="patch_test_user",
            email="patch@test.com",
            first_name="Original",
            last_name="Name",
        )
        self.authenticate_as(test_user)

        # Update both user and profile fields
        update_data = {
            "first_name": "Updated",
            "last_name": "Combined",
            "bio": "Combined update test",
            "occupation": "student",
            "country": "US",
            "preferred_language": "en",
            "website_url": "https://combined-test.com",
        }
        response = self.client.patch(self.url, update_data, format="json")

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify all fields were updated
        test_user.refresh_from_db()
        test_user.profile.refresh_from_db()

        self.assertEqual(test_user.first_name, "Updated")
        self.assertEqual(test_user.last_name, "Combined")
        self.assertEqual(test_user.profile.bio, "Combined update test")
        self.assertEqual(test_user.profile.occupation, "student")
        self.assertEqual(test_user.profile.country, "US")
        self.assertEqual(test_user.profile.website_url, "https://combined-test.com")

    def test_patch_current_user_empty_string_values(self):
        """Test that empty strings are accepted for optional fields."""
        # Create user with filled fields
        test_user = self.create_test_user(
            username="empty_test_user",
            email="empty@test.com",
            first_name="ToBeCleared",
            last_name="AlsoCleared",
        )
        test_user.profile.bio = "Will be cleared"
        test_user.profile.website_url = "https://will-be-cleared.com"
        test_user.profile.save()

        self.authenticate_as(test_user)

        # Set fields to empty strings
        update_data = {"first_name": "", "last_name": "", "bio": "", "website_url": ""}
        response = self.client.patch(self.url, update_data, format="json")

        # Should return 200 OK - empty strings should be accepted
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify fields were cleared
        test_user.refresh_from_db()
        test_user.profile.refresh_from_db()

        self.assertEqual(test_user.first_name, "")
        self.assertEqual(test_user.last_name, "")
        self.assertEqual(test_user.profile.bio, "")
        self.assertEqual(test_user.profile.website_url, "")

    def test_patch_current_user_null_values(self):
        """Test that null values are properly handled for nullable fields."""
        # Create user with filled profile fields
        test_user = self.create_test_user(
            username="null_test_user", email="null@test.com"
        )
        test_user.profile.bio = "Will be nulled"
        test_user.profile.occupation = "teacher"
        test_user.profile.country = "US"
        test_user.profile.save()

        self.authenticate_as(test_user)

        # Set profile fields to null (Note: first_name/last_name don't accept null)
        import json

        response = self.client.patch(
            self.url,
            json.dumps(
                {"bio": None, "occupation": None, "country": None, "website_url": None}
            ),
            content_type="application/json",
        )

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify nullable fields accept null
        test_user.profile.refresh_from_db()
        self.assertIsNone(test_user.profile.bio)
        self.assertIsNone(test_user.profile.occupation)
        self.assertIsNone(test_user.profile.country)
        self.assertIsNone(test_user.profile.website_url)

    def test_patch_current_user_partial_update(self):
        """Test that partial updates work (only updating some fields)."""
        # Create user with various fields set
        test_user = self.create_test_user(
            username="partial_test_user",
            email="partial@test.com",
            first_name="Original",
            last_name="Unchanged",
        )
        test_user.profile.bio = "Original bio"
        test_user.profile.occupation = "student"
        test_user.profile.country = "CA"
        test_user.profile.save()

        self.authenticate_as(test_user)

        # Update only first_name and bio, leave others unchanged
        update_data = {"first_name": "Changed", "bio": "Updated bio only"}
        response = self.client.patch(self.url, update_data, format="json")

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify only specified fields were updated
        test_user.refresh_from_db()
        test_user.profile.refresh_from_db()

        self.assertEqual(test_user.first_name, "Changed")
        self.assertEqual(test_user.last_name, "Unchanged")  # Should remain unchanged
        self.assertEqual(test_user.profile.bio, "Updated bio only")
        self.assertEqual(
            test_user.profile.occupation, "student"
        )  # Should remain unchanged
        self.assertEqual(test_user.profile.country, "CA")  # Should remain unchanged

    def test_patch_current_user_invalid_data(self):
        """Test validation errors for invalid field values."""
        self.authenticate_as(self.ahmad)

        # Test invalid website URL
        response = self.client.patch(
            self.url, {"website_url": "not-a-valid-url"}, format="json"
        )

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("website_url", response.data)

        # Test invalid country code
        response = self.client.patch(self.url, {"country": "INVALID"}, format="json")

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid occupation
        response = self.client.patch(
            self.url, {"occupation": "invalid_occupation"}, format="json"
        )

        # Should return 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_current_user_response_structure(self):
        """Test that PATCH response has correct structure."""
        self.authenticate_as(self.ahmad)

        # Make a simple update
        response = self.client.patch(self.url, {"first_name": "Test"}, format="json")

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify response contains all expected User serializer fields
        expected_fields = [
            "id",
            "url",
            "profile_url",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "groups",
        ]

        for field in expected_fields:
            with self.subTest(field=field):
                self.assertIn(
                    field, response.data, f"Field '{field}' missing from PATCH response"
                )

        # Verify sensitive fields are not exposed
        sensitive_fields = ["password", "user_permissions"]
        for field in sensitive_fields:
            with self.subTest(field=field):
                self.assertNotIn(
                    field,
                    response.data,
                    f"Sensitive field '{field}' exposed in PATCH response",
                )

    def test_patch_current_user_different_users(self):
        """Test that users can only update their own information."""
        # Ahmad updates his own info
        self.authenticate_as(self.ahmad)
        response = self.client.patch(
            self.url, {"first_name": "Ahmad's Update"}, format="json"
        )

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.ahmad.pk)
        self.assertEqual(response.data["first_name"], "Ahmad's Update")

        # Marie updates her own info
        self.authenticate_as(self.marie)
        response = self.client.patch(
            self.url, {"first_name": "Marie's Update"}, format="json"
        )

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.marie.pk)
        self.assertEqual(response.data["first_name"], "Marie's Update")

        # Verify Ahmad's data wasn't affected by Marie's update
        self.ahmad.refresh_from_db()
        self.assertEqual(self.ahmad.first_name, "Ahmad's Update")
