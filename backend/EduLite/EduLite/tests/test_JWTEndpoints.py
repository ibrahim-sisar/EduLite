from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = (
    get_user_model()
)  # Use this to get your User model, whether it's Django's default or custom


class TestJWTEndpoints(APITestCase):
    def setUp(self):
        # This method is called before each test.
        # Good place to create a test user.
        self.username = "testuser"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            username=self.username, password=self.password, email="testuser@example.com"
        )

        # URLs for the token endpoints
        # It's good practice to use reverse() to get URLs to avoid hardcoding
        self.token_obtain_url = reverse("token_obtain_pair")
        self.token_refresh_url = reverse("token_refresh")

    # --- Tests for TokenObtainPairView (/api/token/) ---

    def test_obtain_token_pair_success(self):
        data = {"username": self.username, "password": self.password}
        response = self.client.post(self.token_obtain_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        self.assertTrue("refresh" in response.data)
        # You could add more assertions, like checking if the tokens are non-empty strings

    def test_obtain_token_pair_invalid_credentials(self):
        data = {"username": self.username, "password": "wrongpassword"}
        response = self.client.post(self.token_obtain_url, data, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # SimpleJWT returns 401 for bad creds
        self.assertFalse("access" in response.data)

    def test_obtain_token_pair_nonexistent_user(self):
        data = {"username": "nonexistentuser", "password": "anypassword"}
        response = self.client.post(self.token_obtain_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_pair_missing_username(self):
        data = {"password": self.password}
        response = self.client.post(self.token_obtain_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "username" in response.data
        )  # Check for error message related to username

    def test_obtain_token_pair_missing_password(self):
        data = {"username": self.username}
        response = self.client.post(self.token_obtain_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "password" in response.data
        )  # Check for error message related to password

    # --- Tests for TokenRefreshView (/api/token/refresh/) ---

    def test_refresh_token_success(self):
        # First, get an initial pair of tokens
        obtain_data = {"username": self.username, "password": self.password}
        obtain_response = self.client.post(
            self.token_obtain_url, obtain_data, format="json"
        )
        self.assertEqual(obtain_response.status_code, status.HTTP_200_OK)
        refresh_token = obtain_response.data["refresh"]
        original_access_token = obtain_response.data["access"]

        # Now, use the refresh token
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(
            self.token_refresh_url, refresh_data, format="json"
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in refresh_response.data)
        self.assertNotEqual(
            original_access_token, refresh_response.data["access"]
        )  # New access token
        # ROTATE_REFRESH_TOKENS is True, so a new refresh token must be returned
        self.assertIn("refresh", refresh_response.data)
        self.assertNotEqual(refresh_token, refresh_response.data["refresh"])

    def test_refresh_token_blacklisted_after_rotation(self):
        """Old refresh token should be blacklisted after rotation and rejected on reuse."""
        # Get initial tokens
        obtain_data = {"username": self.username, "password": self.password}
        obtain_response = self.client.post(
            self.token_obtain_url, obtain_data, format="json"
        )
        old_refresh_token = obtain_response.data["refresh"]

        # Use the refresh token (this rotates it and blacklists the old one)
        refresh_response = self.client.post(
            self.token_refresh_url, {"refresh": old_refresh_token}, format="json"
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)

        # Try to reuse the old (now blacklisted) refresh token
        reuse_response = self.client.post(
            self.token_refresh_url, {"refresh": old_refresh_token}, format="json"
        )
        self.assertEqual(reuse_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_invalid_or_expired(self):
        invalid_refresh_data = {"refresh": "this.is.an.invalid.token"}
        response = self.client.post(
            self.token_refresh_url, invalid_refresh_data, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # SimpleJWT returns 401 for bad refresh token

    def test_refresh_token_missing(self):
        response = self.client.post(
            self.token_refresh_url, {}, format="json"
        )  # Empty data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "refresh" in response.data
        )  # Check for error message related to refresh token
