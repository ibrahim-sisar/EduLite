# users/tests/functions/test__create_single_dummy_user.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from unittest.mock import patch, MagicMock

from ...management.logic import _create_single_dummy_user

User = get_user_model()

# Define the full path to the faker utils as used in your logic.py file for patching
FAKER_UTILS_PATH = 'users.management.utils.faker_utils'

class CreateSingleDummyUserTests(TestCase):
    """
    Test suite for the _create_single_dummy_user helper function.
    """

    def setUp(self):
        """Set up a dummy config dictionary for tests."""
        self.dummy_config = {
            'country_options': ['CA', 'US'],
            'occupation_options': ['Developer', 'Student'],
            'language_options': ['en', 'fr'],
            'dummy_picture_paths': ['path/to/pic1.png'],
        }
        self.dummy_password = "password123"

    @patch(f'{FAKER_UTILS_PATH}.get_random_profile_picture_path')
    @patch(f'{FAKER_UTILS_PATH}.get_random_language')
    @patch(f'{FAKER_UTILS_PATH}.get_random_country')
    @patch(f'{FAKER_UTILS_PATH}.get_random_occupation')
    @patch(f'{FAKER_UTILS_PATH}.get_random_bio')
    @patch(f'{FAKER_UTILS_PATH}.get_random_last_name')
    @patch(f'{FAKER_UTILS_PATH}.get_random_first_name')
    @patch(f'{FAKER_UTILS_PATH}.get_random_email')
    @patch(f'{FAKER_UTILS_PATH}.get_random_username')
    @patch('users.management.logic.User.objects') # Patch the User model's manager
    def test_successful_user_creation(self, mock_user_manager, mock_get_username,
                                      mock_get_email, mock_get_first_name, mock_get_last_name,
                                      mock_get_bio, mock_get_occupation, mock_get_country,
                                      mock_get_language, mock_get_picture_path):
        """
        Test the successful creation of a User and its associated UserProfile.
        """
        # --- Setup Mocks ---
        # Mock return values for faker utils
        mock_get_username.return_value = 'testuser'
        mock_get_email.return_value = 'testuser@example.com'
        mock_get_first_name.return_value = 'Test'
        mock_get_last_name.return_value = 'User'
        mock_get_bio.return_value = 'A test bio.'
        mock_get_occupation.return_value = 'Developer'
        mock_get_country.return_value = 'CA'
        mock_get_language.return_value = 'en'
        mock_get_picture_path.return_value = 'path/to/pic1.png'
        
        # Mock the database checks and creation
        mock_user_manager.filter.return_value.exists.return_value = False # User does not exist
        
        # Mock the created user and its profile
        mock_profile = MagicMock()
        mock_user = MagicMock(spec=User)
        mock_user.profile = mock_profile
        mock_user_manager.create_user.return_value = mock_user

        # --- Action ---
        created_user = _create_single_dummy_user(self.dummy_password, self.dummy_config)

        # --- Assertions ---
        # 1. Check that the existing user check was performed
        mock_user_manager.filter.assert_called_once()
        
        # 2. Check that create_user was called with correct data
        mock_user_manager.create_user.assert_called_once()

        # 3. Check that the function returned the created user object
        self.assertEqual(created_user, mock_user)

    @patch('users.management.logic.User.objects')
    @patch(f'{FAKER_UTILS_PATH}.get_random_username')
    @patch(f'{FAKER_UTILS_PATH}.get_random_email')
    def test_skips_creation_if_user_already_exists(self, mock_get_email, mock_get_username, mock_user_manager):
        """
        Test that the function correctly skips user creation if the username or email already exists.
        """
        # --- Setup Mocks ---
        mock_get_username.return_value = 'existinguser'
        mock_get_email.return_value = 'existing@example.com'
        mock_user_manager.filter.return_value.exists.return_value = True # Simulate user exists

        # --- Action ---
        result = _create_single_dummy_user(self.dummy_password, self.dummy_config)

        # --- Assertions ---
        # 1. Check that the user existence check was performed
        mock_user_manager.filter.assert_called_once()
        # 2. Check that create_user was NOT called
        mock_user_manager.create_user.assert_not_called()
        # 3. Check that the function returned None
        self.assertIsNone(result)

    @patch('users.management.logic.User.objects.create_user', side_effect=IntegrityError("DB constraint failed"))
    @patch('users.management.logic.User.objects.filter')
    @patch(f'{FAKER_UTILS_PATH}.get_random_username')
    @patch(f'{FAKER_UTILS_PATH}.get_random_email')
    def test_handles_integrity_error_gracefully(self, mock_get_email, mock_get_username, mock_filter, mock_create_user):
        """
        Test that the function handles IntegrityError during user creation and returns None.
        """
        # --- Setup Mocks ---
        mock_get_username.return_value = 'someuser'
        mock_get_email.return_value = 'some@example.com'
        mock_filter.return_value.exists.return_value = False # User does not exist

        # --- Action ---
        result = _create_single_dummy_user(self.dummy_password, self.dummy_config)

        # --- Assertions ---
        # 1. Check that create_user was called
        mock_create_user.assert_called_once()
        # 2. Check that the function returned None due to the exception
        self.assertIsNone(result)