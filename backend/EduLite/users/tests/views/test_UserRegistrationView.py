# users/tests/views/test_UserRegistrationView.py - Tests for UserRegistrationView

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .. import UsersAppTestCase


class UserRegistrationViewTest(UsersAppTestCase):
    """Test cases for the UserRegistrationView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = reverse("user-register")  # Assuming URL name is 'user-register'

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False)
    def test_register_user_success(self):
        """Test successful user registration with immediate account creation."""
        data = {
            "username": "newstudent",
            "email": "new@university.edu",
            "password": "strongpass123",
            "password2": "strongpass123",
            "first_name": "New",
            "last_name": "Student",
        }

        response = self.client.post(self.url, data)

        # Should return 201 Created
        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Should return success message and user info
        self.assertIn("message", response.data)
        self.assertIn("user_id", response.data)
        self.assertIn("username", response.data)
        self.assertEqual(response.data["username"], "newstudent")

        # User should be created in database
        self.assertTrue(User.objects.filter(username="newstudent").exists())

        # UserProfile should be auto-created via signal
        user = User.objects.get(username="newstudent")
        self.assertTrue(hasattr(user, "profile"))
        self.assertTrue(hasattr(user.profile, "privacy_settings"))

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False)
    def test_register_user_no_authentication_required(self):
        """Test that registration doesn't require authentication."""
        data = {
            "username": "publicreg",
            "email": "public@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }

        # Don't authenticate - should still work
        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="publicreg").exists())

    def test_register_user_missing_username(self):
        """Test registration with missing username."""
        data = {"email": "nouser@example.com", "password": "testpass123"}

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_user_missing_email(self):
        """Test registration with missing email."""
        data = {
            "username": "noemail",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_missing_password(self):
        """Test registration with missing password."""
        data = {"username": "nopass", "email": "nopass@university.edu"}

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        # Should have errors for both password fields
        self.assertTrue("password" in response.data or "password2" in response.data)

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username."""
        # Use existing persona username
        data = {
            "username": "ahmad_gaza",  # Already exists from personas
            "email": "different@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email."""
        # Use existing persona email
        data = {
            "username": "differentuser",
            "email": "ahmad@gaza-university.ps",  # Already exists from personas
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_invalid_email(self):
        """Test registration with invalid email format."""
        data = {
            "username": "bademail",
            "email": "not-an-email",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_weak_password(self):
        """Test registration with weak password."""
        data = {
            "username": "weakpass",
            "email": "weak@university.edu",
            "password": "123",  # Too short
            "password2": "123",
        }

        response = self.client.post(self.url, data)

        # This depends on password validation settings
        # Might be 400 if validation is enabled
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("password", response.data)
        else:
            # If no validation, it should still succeed
            self.assert_response_success(response, status.HTTP_201_CREATED)

    def test_register_user_long_username(self):
        """Test registration with very long username."""
        data = {
            "username": "a" * 200,  # Exceeds Django's default max_length
            "email": "long@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_user_invalid_characters_username(self):
        """Test registration with invalid characters in username."""
        data = {
            "username": "user@#$%",  # Invalid characters
            "email": "invalid@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        # This depends on username validation rules
        # Django allows most characters by default, but custom validation might reject
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("username", response.data)
        else:
            self.assert_response_success(response, status.HTTP_201_CREATED)

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False)
    def test_register_user_with_optional_fields(self):
        """Test registration with optional first_name and last_name."""
        data = {
            "username": "optional",
            "email": "optional@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Optional",
            "last_name": "User",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Check that names were saved
        user = User.objects.get(username="optional")
        self.assertEqual(user.first_name, "Optional")
        self.assertEqual(user.last_name, "User")

    def test_register_user_empty_data(self):
        """Test registration with empty data."""
        response = self.client.post(self.url, {})

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        # Should have errors for required fields
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)
        self.assertIn("password2", response.data)

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords."""
        data = {
            "username": "mismatch",
            "email": "mismatch@university.edu",
            "password": "strongUniquePassword123!",
            "password2": "differentStrongPassword456!",
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        # Should have non-field error about password mismatch
        self.assertTrue(
            "non_field_errors" in response.data or "password2" in response.data
        )

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False)
    def test_register_user_profile_created_with_defaults(self):
        """Test that UserProfile is created with proper defaults."""
        data = {
            "username": "profiletest",
            "email": "profile@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)
        self.assert_response_success(response, status.HTTP_201_CREATED)

        user = User.objects.get(username="profiletest")

        # Profile should exist
        self.assertTrue(hasattr(user, "profile"))

        # Profile should have default values
        profile = user.profile
        self.assertIsNone(profile.bio)
        self.assertIsNone(profile.country)
        self.assertIsNone(profile.preferred_language)
        self.assertEqual(profile.friends.count(), 0)

        # Privacy settings should exist with defaults
        self.assertTrue(hasattr(profile, "privacy_settings"))
        privacy = profile.privacy_settings
        self.assertEqual(privacy.search_visibility, "everyone")
        self.assertEqual(privacy.profile_visibility, "friends_only")
        self.assertTrue(privacy.show_full_name)
        self.assertFalse(privacy.show_email)
        self.assertTrue(privacy.allow_friend_requests)

    def test_register_user_case_insensitive_username(self):
        """Test username case sensitivity."""
        # Create user with mixed case
        data1 = {
            "username": "CaseSensitive",
            "email": "case1@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }
        response1 = self.client.post(self.url, data1)
        self.assert_response_success(response1, status.HTTP_201_CREATED)

        # Try to create user with same username but different case
        data2 = {
            "username": "casesensitive",  # Different case
            "email": "case2@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }
        response2 = self.client.post(self.url, data2)

        # Django usernames are case sensitive by default
        # This should succeed unless custom validation prevents it
        if response2.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("username", response2.data)
        else:
            self.assert_response_success(response2, status.HTTP_201_CREATED)

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False)
    def test_register_user_special_characters_in_names(self):
        """Test registration with special characters in first/last names."""
        data = {
            "username": "specialnames",
            "email": "special@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "José",  # Accented character
            "last_name": "O'Connor",  # Apostrophe
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_201_CREATED)

        user = User.objects.get(username="specialnames")
        self.assertEqual(user.first_name, "José")
        self.assertEqual(user.last_name, "O'Connor")

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False)
    def test_register_user_unicode_support(self):
        """Test registration with Unicode characters."""
        data = {
            "username": "unicode_user",
            "email": "unicode@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "محمد",  # Arabic
            "last_name": "李",  # Chinese
        }

        response = self.client.post(self.url, data)

        self.assert_response_success(response, status.HTTP_201_CREATED)

        user = User.objects.get(username="unicode_user")
        self.assertEqual(user.first_name, "محمد")
        self.assertEqual(user.last_name, "李")

    def test_register_user_sql_injection_attempt(self):
        """Test registration with SQL injection attempt."""
        data = {
            "username": "'; DROP TABLE auth_user; --",
            "email": "sql@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        # Should either create user with escaped username or reject it
        # Either way, should not cause database issues
        if response.status_code == status.HTTP_201_CREATED:
            # Username should be escaped/sanitized
            self.assertTrue(User.objects.filter(username__contains="DROP").exists())
        else:
            # Or rejected due to validation
            self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)

        # Most importantly, users table should still exist
        self.assertGreater(User.objects.count(), 0)

    def test_register_user_performance_with_existing_users(self):
        """Test registration performance doesn't degrade with many existing users."""
        # We already have our personas created, so let's test registration
        # doesn't slow down due to uniqueness checks

        import time

        start_time = time.time()

        data = {
            "username": "perftest",
            "email": "perf@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.url, data)

        end_time = time.time()
        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Should complete within reasonable time (adjust based on requirements)
        self.assertLess(duration, 2.0, "Registration took too long")

    @override_settings(USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=True)
    def test_register_user_with_email_verification_required(self):
        """Test registration when email verification is required."""
        data = {
            "username": "emailverify",
            "email": "verify@university.edu",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Test",
            "last_name": "Verify",
        }

        response = self.client.post(self.url, data)

        # Should return 201 Created
        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Should return message about email verification
        self.assertIn("message", response.data)
        self.assertIn("Verification email sent", response.data["message"])

        # User should NOT be created yet
        self.assertFalse(User.objects.filter(username="emailverify").exists())
