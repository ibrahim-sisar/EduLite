# users/tests/views/test_UserProfilePrivacySettingsChoicesView.py - Tests for UserProfilePrivacySettingsChoicesView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase


class UserProfilePrivacySettingsChoicesViewTest(UsersAppTestCase):
    """Test cases for the UserProfilePrivacySettingsChoicesView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = reverse("privacy-settings-choices")

    # --- Authentication Tests ---

    def test_get_privacy_choices_requires_authentication(self):
        """Test that getting privacy choices requires authentication."""
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- Success Cases ---

    def test_get_privacy_choices_success(self):
        """Test successfully retrieving privacy setting choices."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check that response contains expected choice categories
        self.assertIn("search_visibility", response.data)
        self.assertIn("profile_visibility", response.data)

    def test_search_visibility_choices(self):
        """Test that search visibility choices are complete and correct."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        search_choices = response.data.get("search_visibility", [])

        # Should have expected choices
        choice_values = [choice["value"] for choice in search_choices]
        self.assertIn("everyone", choice_values)
        self.assertIn("friends_only", choice_values)
        self.assertIn("friends_of_friends", choice_values)
        self.assertIn("nobody", choice_values)

        # Each choice should have value and display name
        for choice in search_choices:
            self.assertIn("value", choice)
            self.assertIn("display_name", choice)
            self.assertIsInstance(choice["value"], str)
            self.assertIsInstance(choice["display_name"], str)

    def test_profile_visibility_choices(self):
        """Test that profile visibility choices are complete and correct."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        profile_choices = response.data.get("profile_visibility", [])

        # Should have expected choices
        choice_values = [choice["value"] for choice in profile_choices]
        self.assertIn("public", choice_values)
        self.assertIn("friends_only", choice_values)
        self.assertIn("private", choice_values)

        # Each choice should have proper structure
        for choice in profile_choices:
            self.assertIn("value", choice)
            self.assertIn("display_name", choice)

    def test_boolean_field_choices(self):
        """Test that boolean fields have proper choice representation."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Boolean fields might be included
        if "show_full_name" in response.data:
            choices = response.data["show_full_name"]
            self.assertEqual(len(choices), 2)  # True/False

            values = [choice["value"] for choice in choices]
            self.assertIn(True, values)
            self.assertIn(False, values)

    # --- Localization Tests ---

    def test_choices_display_names_are_readable(self):
        """Test that display names are human-readable."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check search visibility display names
        search_choices = response.data.get("search_visibility", [])
        for choice in search_choices:
            # Display names should be properly formatted
            self.assertNotEqual(choice["display_name"], choice["value"])
            self.assertNotIn("_", choice["display_name"])  # No underscores

            # Check specific display names
            if choice["value"] == "everyone":
                self.assertIn("Everyone", choice["display_name"])
            elif choice["value"] == "friends_only":
                self.assertIn("Friends", choice["display_name"])

    def test_choices_with_language_header(self):
        """Test that choices respect language preferences if implemented."""
        self.authenticate_as(self.ahmad)

        # Try with Arabic language preference (Ahmad's preference)
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE="ar")
        self.assert_response_success(response, status.HTTP_200_OK)

        # Choices should still be returned (even if not translated)
        self.assertIn("search_visibility", response.data)

    # --- Caching Tests ---

    def test_choices_are_consistent(self):
        """Test that choices remain consistent across requests."""
        self.authenticate_as(self.ahmad)

        # First request
        response1 = self.client.get(self.url)
        self.assert_response_success(response1, status.HTTP_200_OK)

        # Second request
        response2 = self.client.get(self.url)
        self.assert_response_success(response2, status.HTTP_200_OK)

        # Choices should be identical
        self.assertEqual(response1.data, response2.data)

    # --- All Users Access ---

    def test_all_authenticated_users_see_same_choices(self):
        """Test that all users see the same privacy choices."""
        # Test with different users
        users = [self.ahmad, self.marie, self.joy, self.sarah_teacher]

        responses = []
        for user in users:
            self.authenticate_as(user)
            response = self.client.get(self.url)
            self.assert_response_success(response, status.HTTP_200_OK)
            responses.append(response.data)

        # All users should see identical choices
        for i in range(1, len(responses)):
            self.assertEqual(responses[0], responses[i])

    # --- HTTP Method Tests ---

    def test_only_get_method_allowed(self):
        """Test that only GET method is allowed for choices endpoint."""
        self.authenticate_as(self.ahmad)

        # Try POST
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try PUT
        response = self.client.put(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try PATCH
        response = self.client.patch(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try DELETE
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # --- Response Format Tests ---

    def test_choices_response_format(self):
        """Test the overall format of the choices response."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Response should be a dictionary
        self.assertIsInstance(response.data, dict)

        # Each field should map to a list of choices
        for field_name, choices in response.data.items():
            self.assertIsInstance(choices, list)
            self.assertGreater(len(choices), 0)  # Should have at least one choice

    def test_choices_include_descriptions(self):
        """Test if choices include helpful descriptions."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check if descriptions are included (optional feature)
        search_choices = response.data.get("search_visibility", [])
        if search_choices and "description" in search_choices[0]:
            for choice in search_choices:
                self.assertIn("description", choice)
                self.assertIsInstance(choice["description"], str)
                self.assertGreater(len(choice["description"]), 0)

    # --- Performance Test ---

    def test_choices_endpoint_performance(self):
        """Test that choices endpoint responds quickly."""
        self.authenticate_as(self.ahmad)

        import time

        start_time = time.time()

        # Make multiple requests
        for _ in range(10):
            response = self.client.get(self.url)
            self.assert_response_success(response, status.HTTP_200_OK)

        end_time = time.time()
        duration = end_time - start_time

        # Should be very fast (choices are static)
        self.assertLess(duration, 1.0, "Choices endpoint too slow")

    # --- Use Case Test ---

    def test_choices_match_model_field_choices(self):
        """Test that API choices match the model field choices."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Get model field choices
        from ...models import UserProfilePrivacySettings

        # Compare with model choices if accessible
        if hasattr(UserProfilePrivacySettings, "SEARCH_VISIBILITY_CHOICES"):
            model_choices = dict(UserProfilePrivacySettings.SEARCH_VISIBILITY_CHOICES)
            api_choices = {
                choice["value"]: choice["display_name"]
                for choice in response.data.get("search_visibility", [])
            }

            # API should have all model choices
            for value in model_choices.keys():
                self.assertIn(value, api_choices)
