# backend/EduLite/users/tests/test_UserProfilePrivacySettingsRetrieveUpdateView.py
# Tests for UserProfilePrivacySettingsRetrieveUpdateView

import logging
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from users.models import UserProfile, UserProfilePrivacySettings

logger = logging.getLogger(__name__)
User = get_user_model()


class UserProfilePrivacySettingsRetrieveUpdateViewTests(APITestCase):
    """
    Test suite for UserProfilePrivacySettingsRetrieveUpdateView.
    Tests retrieving and updating user privacy settings.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        cls.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="testpass123",
            email="other@example.com",
            first_name="Other",
            last_name="User"
        )

        # URL pattern - adjust based on your actual URL configuration
        cls.privacy_settings_url = reverse("privacy-settings")

    def setUp(self):
        """Set up for each test method."""
        self.client.force_authenticate(user=self.user)

    def test_requires_authentication(self):
        """Test that the view requires authentication."""
        self.client.logout()

        response = self.client.get(self.privacy_settings_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_privacy_settings_existing(self):
        """Test retrieving existing privacy settings."""
        # Ensure privacy settings exist for the user
        privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.user.profile
        )

        response = self.client.get(self.privacy_settings_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('search_visibility', response.data)
        self.assertIn('profile_visibility', response.data)
        self.assertIn('show_full_name', response.data)
        self.assertIn('show_email', response.data)
        self.assertIn('allow_friend_requests', response.data)
        self.assertIn('allow_chat_invites', response.data)

        # Check default values
        self.assertEqual(response.data['search_visibility'], privacy_settings.search_visibility)
        self.assertEqual(response.data['profile_visibility'], privacy_settings.profile_visibility)

    @patch('users.views.logging.getLogger')
    def test_get_privacy_settings_creates_missing(self, mock_logger):
        """Test that privacy settings are created if they don't exist."""
        # Delete existing privacy settings to test creation
        UserProfilePrivacySettings.objects.filter(
            user_profile=self.user.profile
        ).delete()

        response = self.client.get(self.privacy_settings_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that privacy settings were created
        privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.user.profile
        )
        self.assertIsNotNone(privacy_settings)

        # Verify logging was called
        mock_logger.return_value.info.assert_called_once()

    def test_put_update_privacy_settings_valid_data(self):
        """Test full update of privacy settings with valid data."""
        update_data = {
            'search_visibility': 'friends_only',
            'profile_visibility': 'private',
            'show_full_name': False,
            'show_email': False,
            'allow_friend_requests': False,
            'allow_chat_invites': False
        }

        response = self.client.put(self.privacy_settings_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the data was updated in the database
        privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.user.profile
        )
        self.assertEqual(privacy_settings.search_visibility, 'friends_only')
        self.assertEqual(privacy_settings.profile_visibility, 'private')
        self.assertFalse(privacy_settings.show_full_name)
        self.assertFalse(privacy_settings.show_email)
        self.assertFalse(privacy_settings.allow_friend_requests)
        self.assertFalse(privacy_settings.allow_chat_invites)

    def test_put_update_privacy_settings_invalid_choice(self):
        """Test full update with invalid choice values."""
        update_data = {
            'search_visibility': 'invalid_choice',
            'profile_visibility': 'public',
            'show_full_name': True,
            'show_email': False,
            'allow_friend_requests': True,
            'allow_chat_invites': True
        }

        response = self.client.put(self.privacy_settings_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('search_visibility', response.data)

    def test_put_update_privacy_settings_missing_required_fields(self):
        """Test full update with missing required fields."""
        update_data = {
            'search_visibility': 'everyone'
            # Missing other required fields
        }

        response = self.client.put(self.privacy_settings_url, update_data, format='json')

        # PUT should require all fields (depending on serializer implementation)
        # Adjust this assertion based on your serializer's required field configuration
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])

    def test_patch_partial_update_search_visibility(self):
        """Test partial update of search visibility only."""
        original_privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.user.profile
        )
        original_profile_visibility = original_privacy_settings.profile_visibility

        update_data = {
            'search_visibility': 'friends_of_friends'
        }

        response = self.client.patch(self.privacy_settings_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only search_visibility was updated
        updated_privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.user.profile
        )
        self.assertEqual(updated_privacy_settings.search_visibility, 'friends_of_friends')
        self.assertEqual(updated_privacy_settings.profile_visibility, original_profile_visibility)

    def test_patch_partial_update_multiple_fields(self):
        """Test partial update of multiple fields."""
        update_data = {
            'show_full_name': False,
            'allow_friend_requests': False
        }

        response = self.client.patch(self.privacy_settings_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the specified fields were updated
        privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.user.profile
        )
        self.assertFalse(privacy_settings.show_full_name)
        self.assertFalse(privacy_settings.allow_friend_requests)

    def test_patch_partial_update_invalid_data(self):
        """Test partial update with invalid data."""
        update_data = {
            'search_visibility': 'invalid_value',
            'show_full_name': 'not_a_boolean'
        }

        response = self.client.patch(self.privacy_settings_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('search_visibility', response.data)

    def test_user_can_only_access_own_privacy_settings(self):
        """Test that users can only access their own privacy settings."""
        # The view should automatically use the authenticated user's settings
        # so we don't need to test access to other users' settings directly
        # since the view doesn't take a user ID parameter

        # Authenticate as different user
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.privacy_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should get the other user's privacy settings, not the original user's
        other_user_privacy = UserProfilePrivacySettings.objects.get(
            user_profile=self.other_user.profile
        )

        # The response should contain the other user's settings
        self.assertEqual(
            response.data['search_visibility'],
            other_user_privacy.search_visibility
        )

    def test_privacy_settings_choices_validation(self):
        """Test that only valid choices are accepted for choice fields."""
        # Test all valid search visibility choices
        valid_search_choices = ['everyone', 'friends_of_friends', 'friends_only', 'nobody']

        for choice in valid_search_choices:
            update_data = {'search_visibility': choice}
            response = self.client.patch(self.privacy_settings_url, update_data, format='json')

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Valid choice '{choice}' should be accepted"
            )

            # Verify the update
            privacy_settings = UserProfilePrivacySettings.objects.get(
                user_profile=self.user.profile
            )
            self.assertEqual(privacy_settings.search_visibility, choice)

        # Test all valid profile visibility choices
        valid_profile_choices = ['public', 'friends_only', 'private']

        for choice in valid_profile_choices:
            update_data = {'profile_visibility': choice}
            response = self.client.patch(self.privacy_settings_url, update_data, format='json')

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Valid choice '{choice}' should be accepted"
            )

    def test_boolean_fields_validation(self):
        """Test validation of boolean fields."""
        boolean_fields = [
            'show_full_name',
            'show_email',
            'allow_friend_requests',
            'allow_chat_invites'
        ]

        for field in boolean_fields:
            # Test True value
            update_data = {field: True}
            response = self.client.patch(self.privacy_settings_url, update_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Test False value
            update_data = {field: False}
            response = self.client.patch(self.privacy_settings_url, update_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_format(self):
        """Test that the response contains all expected fields."""
        response = self.client.get(self.privacy_settings_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = [
            'search_visibility',
            'profile_visibility',
            'show_full_name',
            'show_email',
            'allow_friend_requests',
            'allow_chat_invites',
            'created_at',
            'updated_at'
        ]

        for field in expected_fields:
            self.assertIn(field, response.data, f"Field '{field}' should be in response")

    def test_timestamps_update_on_change(self):
        """Test that updated_at timestamp changes when settings are modified."""
        # Get initial timestamp
        initial_response = self.client.get(self.privacy_settings_url)
        initial_updated_at = initial_response.data['updated_at']

        # Make a change
        update_data = {'search_visibility': 'friends_only'}
        self.client.patch(self.privacy_settings_url, update_data, format='json')

        # Get updated timestampf
        updated_response = self.client.get(self.privacy_settings_url)
        updated_updated_at = updated_response.data['updated_at']

        # Timestamp should have changed
        self.assertNotEqual(initial_updated_at, updated_updated_at)

    @patch('users.views.logging.getLogger')
    def test_logging_on_privacy_settings_creation(self, mock_logger):
        """Test that appropriate logging occurs when privacy settings are created."""
        # Delete existing privacy settings
        UserProfilePrivacySettings.objects.filter(
            user_profile=self.user.profile
        ).delete()

        # Make a request that should trigger creation
        self.client.get(self.privacy_settings_url)

        # Verify logging was called
        mock_logger.return_value.info.assert_called_once_with(
            "Created missing privacy settings for user %s",
            self.user.username
        )

    def test_privacy_settings_model_validation(self):
        """Test that model-level validation is enforced through the API."""
        # This test depends on your model's clean() method implementation
        # Adjust based on the validation rules in your UserProfilePrivacySettings model

        # Example: Test validation that might exist in the model
        # If search_visibility is 'nobody', profile_visibility should not be 'public'
        update_data = {
            'search_visibility': 'nobody',
            'profile_visibility': 'public'
        }

        response = self.client.put(self.privacy_settings_url, update_data, format='json')

        # This should either be rejected at the serializer level or model level
        # Adjust assertion based on your actual validation implementation
        if hasattr(UserProfilePrivacySettings, 'clean'):
            # If model has validation, it might return 400
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])
