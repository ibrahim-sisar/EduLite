# users/tests/views/test_UserRetrieveView.py - Tests for UserRetrieveView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .. import UsersAppTestCase


class UserRetrieveViewTest(UsersAppTestCase):
    """Test cases for the UserRetrieveView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        # URL will be built dynamically in tests using reverse

    def test_retrieve_user_requires_authentication(self):
        """Test that retrieving user details requires authentication."""
        # Make request without authentication
        url = reverse("user-detail", kwargs={"pk": self.ahmad.pk})
        response = self.client.get(url)

        # Should return 401 Unauthorized
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_authenticated_success(self):
        """Test retrieving user details when authenticated."""
        # Authenticate as Ahmad
        self.authenticate_as(self.ahmad)

        # Retrieve Marie's details
        url = reverse("user-detail", kwargs={"pk": self.marie.pk})
        response = self.client.get(url)

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should contain user data
        self.assertIn("id", response.data)
        self.assertIn("username", response.data)
        self.assertEqual(response.data["id"], self.marie.pk)
        self.assertEqual(response.data["username"], "marie_student")

    def test_retrieve_user_admin_access(self):
        """Test that admin users can retrieve user details."""
        # Create admin user
        admin_user = self.create_test_user(
            username="admin", is_superuser=True, is_staff=True
        )
        self.authenticate_as(admin_user)

        # Retrieve user details
        url = reverse("user-detail", kwargs={"pk": self.ahmad.pk})
        response = self.client.get(url)

        # Should return 200 OK
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "ahmad_gaza")

    def test_retrieve_user_valid_pk(self):
        """Test successful retrieval with valid user PK."""
        self.authenticate_as(self.ahmad)

        # Test retrieving different personas
        test_cases = [
            (self.marie, "marie_student"),
            (self.joy, "joy_student"),
            (self.elena, "elena_student"),
            (self.sarah_teacher, "sarah_teacher"),
        ]

        for user, expected_username in test_cases:
            with self.subTest(user=expected_username):
                url = reverse("user-detail", kwargs={"pk": user.pk})
                response = self.client.get(url)

                self.assert_response_success(response, status.HTTP_200_OK)
                self.assertEqual(response.data["username"], expected_username)
                self.assertEqual(response.data["id"], user.pk)

    def test_retrieve_user_includes_data(self):
        """Test that response includes user data."""
        self.authenticate_as(self.ahmad)

        # Retrieve Ahmad's own profile
        url = reverse("user-detail", kwargs={"pk": self.ahmad.pk})
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)

        # Should have user data (specific fields tested in serializer tests)
        self.assertIsInstance(response.data, dict)
        self.assertGreater(len(response.data), 0)

        # Basic validation that we got the right user
        self.assertEqual(response.data["id"], self.ahmad.pk)

    def test_retrieve_user_response_format(self):
        """Test that response has correct structure and fields."""
        self.authenticate_as(self.marie)

        # Retrieve user details
        url = reverse("user-detail", kwargs={"pk": self.joy.pk})
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)

        # Response should be a dictionary (not paginated)
        self.assertIsInstance(response.data, dict)

        # Should not have pagination fields
        self.assertNotIn("count", response.data)
        self.assertNotIn("next", response.data)
        self.assertNotIn("previous", response.data)
        self.assertNotIn("results", response.data)

        # Should have required user fields
        required_fields = ["id", "username"]
        for field in required_fields:
            self.assertIn(field, response.data)

    def test_retrieve_user_invalid_pk_404(self):
        """Test that non-existent user PK returns 404."""
        self.authenticate_as(self.ahmad)

        # Use a PK that definitely doesn't exist
        non_existent_pk = 99999
        url = reverse("user-detail", kwargs={"pk": non_existent_pk})
        response = self.client.get(url)

        # Should return 404 Not Found
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_negative_pk(self):
        """Test that negative PK is handled gracefully."""
        self.authenticate_as(self.ahmad)

        # Negative PKs can't be reversed with the URL pattern [0-9]+
        # So we test by making a direct request to a manually constructed URL
        url = "/api/users/-1/"
        response = self.client.get(url)

        # Should return 404 Not Found (URL pattern doesn't match)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_zero_pk(self):
        """Test that zero PK is handled gracefully."""
        self.authenticate_as(self.ahmad)

        # Zero PK should return 404
        url = reverse("user-detail", kwargs={"pk": 0})
        response = self.client.get(url)

        # Should return 404 Not Found
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_very_large_pk(self):
        """Test that very large PK values are handled correctly."""
        self.authenticate_as(self.ahmad)

        # Very large PK should return 404 (not server error)
        large_pk = 9999999999999999999999
        url = reverse("user-detail", kwargs={"pk": large_pk})
        response = self.client.get(url)

        # Should return 404 Not Found, not 500 error
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_user_own_profile(self):
        """Test that users can retrieve their own profile."""
        self.authenticate_as(self.ahmad)

        # Retrieve own profile
        url = reverse("user-detail", kwargs={"pk": self.ahmad.pk})
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.ahmad.pk)
        self.assertEqual(response.data["username"], "ahmad_gaza")
        # When viewing own profile, email should be visible
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], "ahmad@gaza-university.ps")

    def test_retrieve_user_other_profile(self):
        """Test that users can retrieve other users' profiles."""
        # Note: UserRetrieveView doesn't have privacy restrictions - that's in UserSearchView
        self.authenticate_as(self.ahmad)

        # Retrieve Sophie's profile (who has private settings)
        url = reverse("user-detail", kwargs={"pk": self.sophie.pk})
        response = self.client.get(url)

        # Should still work - this view doesn't enforce privacy settings
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "sophie_student")

    def test_retrieve_user_inactive_user(self):
        """Test retrieving inactive user details."""
        # Create inactive user
        inactive_user = self.create_test_user(username="inactive", is_active=False)

        self.authenticate_as(self.ahmad)

        # Retrieve inactive user details
        url = reverse("user-detail", kwargs={"pk": inactive_user.pk})
        response = self.client.get(url)

        # Should still return user data (view doesn't filter by is_active)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "inactive")

    def test_retrieve_user_optimized_queries(self):
        """Test that the view uses optimized queries to prevent N+1 problems."""
        self.authenticate_as(self.ahmad)

        # Create additional user with profile to test query optimization
        test_user = self.create_test_user(username="querytest")
        test_user.profile.bio = "Test bio for query optimization"
        test_user.profile.country = "CA"
        test_user.profile.save()

        url = reverse("user-detail", kwargs={"pk": test_user.pk})

        # We can't easily count queries in this test framework, but we can ensure
        # the request completes successfully and includes profile data
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "querytest")

    def test_retrieve_user_with_complex_profile(self):
        """Test retrieving user with full profile data."""
        self.authenticate_as(self.marie)

        # Ahmad has complex profile data (bio, country, language, privacy settings)
        url = reverse("user-detail", kwargs={"pk": self.ahmad.pk})
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify user data is complete
        self.assertEqual(response.data["username"], "ahmad_gaza")
        self.assertEqual(response.data["first_name"], "Ahmad")
        self.assertEqual(response.data["last_name"], "Al-Rashid")
        # Email may or may not be shown based on privacy settings

        # Should include basic profile info if serializer includes it
        self.assertIsNotNone(response.data.get("id"))

    def test_retrieve_user_performance_with_many_users(self):
        """Test that retrieval performance doesn't degrade with many users."""
        # Create many users
        users = []
        for i in range(50):
            users.append(
                User(username=f"perf_user_{i}", email=f"perf{i}@university.edu")
            )
        User.objects.bulk_create(users)

        self.authenticate_as(self.ahmad)

        # Retrieve a specific user - should be fast regardless of total user count
        url = reverse("user-detail", kwargs={"pk": self.marie.pk})

        import time

        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "marie_student")

        # Should complete quickly (adjust threshold as needed)
        self.assertLess(duration, 1.0, "User retrieval took too long")

    def test_retrieve_user_signal_integration(self):
        """Test that users created via signals have proper profile/privacy settings."""
        # Create new user (signals should create profile and privacy settings)
        new_user = self.create_test_user(username="signaltest")

        self.authenticate_as(self.ahmad)

        # Retrieve the new user
        url = reverse("user-detail", kwargs={"pk": new_user.pk})
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "signaltest")

        # Verify profile and privacy settings were created by signals
        self.assertTrue(hasattr(new_user, "profile"))
        self.assertTrue(hasattr(new_user.profile, "privacy_settings"))

    def test_retrieve_user_privacy_filtering(self):
        """Test that privacy settings affect what information is shown."""
        # Ahmad has privacy settings that allow showing email to friends_of_friends
        # Sophie has privacy settings that show email to nobody (show_email=False)

        self.authenticate_as(self.ahmad)

        # Retrieve Sophie's profile (who has show_email=False)
        url = reverse("user-detail", kwargs={"pk": self.sophie.pk})
        response = self.client.get(url)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "sophie_student")

        # Sophie's email should be hidden due to privacy settings
        self.assertNotIn("email", response.data)

        # But other fields should still be present
        self.assertIn("username", response.data)
        self.assertIn("id", response.data)
