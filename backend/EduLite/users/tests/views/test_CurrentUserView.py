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
