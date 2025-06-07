from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock, call

from ...management.logic import generate_dummy_users_data

User = get_user_model()

# Define the full path to the logic module for patching
LOGIC_MODULE_PATH = 'users.management.logic'

class GenerateDummyUsersDataTests(TestCase):
    """
    Test suite for the generate_dummy_users_data orchestrator function.
    """

    @patch(f'{LOGIC_MODULE_PATH}.establish_random_friendships')
    @patch(f'{LOGIC_MODULE_PATH}._create_single_dummy_user')
    @patch(f'{LOGIC_MODULE_PATH}._prepare_dummy_data_config')
    def test_orchestration_flow_with_all_successful_creations(
        self, mock_prepare_config, mock_create_user, mock_establish_friendships
    ):
        """
        Test the main orchestration flow when all user creations succeed.
        """
        # --- Setup Mocks ---
        # Mock the return value of the config helper
        dummy_config = {'some_key': 'some_value'}
        mock_prepare_config.return_value = dummy_config
        
        # Mock the return value of the user creation helper
        # It should return a new mock user object each time it's called
        num_to_create = 5
        mock_users = [MagicMock(spec=User) for _ in range(num_to_create)]
        mock_create_user.side_effect = mock_users

        # --- Action ---
        created_count, failed_count = generate_dummy_users_data(
            num_users=num_to_create, password='testpassword'
        )

        # --- Assertions ---
        # 1. Assert config helper was called once
        mock_prepare_config.assert_called_once()
        
        # 2. Assert user creation helper was called the correct number of times
        self.assertEqual(mock_create_user.call_count, num_to_create)
        # Verify it was called with the correct password and config each time
        mock_create_user.assert_called_with('testpassword', dummy_config)
        
        # 3. Assert the friendship function was called with the list of created users
        mock_establish_friendships.assert_called_once_with(mock_users)

        # 4. Assert the final counts are correct
        self.assertEqual(created_count, 5)
        self.assertEqual(failed_count, 0)

    @patch(f'{LOGIC_MODULE_PATH}.establish_random_friendships')
    @patch(f'{LOGIC_MODULE_PATH}._create_single_dummy_user')
    @patch(f'{LOGIC_MODULE_PATH}._prepare_dummy_data_config')
    def test_orchestration_flow_with_some_failed_creations(
        self, mock_prepare_config, mock_create_user, mock_establish_friendships
    ):
        """
        Test the main orchestration flow when some user creations fail (return None).
        """
        # --- Setup Mocks ---
        mock_prepare_config.return_value = {'some_key': 'some_value'}
        
        # Mock the user creation helper to return a mix of successful users and failures (None)
        mock_user1 = MagicMock(spec=User)
        mock_user2 = MagicMock(spec=User)
        mock_create_user.side_effect = [mock_user1, None, mock_user2, None, None]
        
        num_to_attempt = 5

        # --- Action ---
        created_count, failed_count = generate_dummy_users_data(
            num_users=num_to_attempt, password='testpassword'
        )
        
        # --- Assertions ---
        # 1. Assert user creation was attempted 5 times
        self.assertEqual(mock_create_user.call_count, num_to_attempt)
        
        # 2. Assert friendship function was called only with the successfully created users
        successfully_created_users = [mock_user1, mock_user2]
        mock_establish_friendships.assert_called_once_with(successfully_created_users)
        
        # 3. Assert the final counts are correct
        self.assertEqual(created_count, 2)
        self.assertEqual(failed_count, 3)

    @patch(f'{LOGIC_MODULE_PATH}.establish_random_friendships')
    @patch(f'{LOGIC_MODULE_PATH}._create_single_dummy_user')
    @patch(f'{LOGIC_MODULE_PATH}._prepare_dummy_data_config')
    def test_friendship_step_is_called_with_one_user(
        self, mock_prepare_config, mock_create_user, mock_establish_friendships
    ):
        """
        Test that the friendship step is still called when only one user is created.
        (The inner logic of establish_random_friendships will handle the case of < 2 users).
        """
        # --- Setup Mocks ---
        mock_prepare_config.return_value = {}
        mock_user1 = MagicMock(spec=User)
        mock_create_user.side_effect = [mock_user1, None, None] # Only one user is successfully created

        # --- Action ---
        created_count, failed_count = generate_dummy_users_data(num_users=3, password='pw')

        # --- Assertions ---
        # The orchestrator should call establish_random_friendships with the list of created users,
        # regardless of its size. The called function is responsible for handling the list.
        mock_establish_friendships.assert_called_once_with([mock_user1])
        self.assertEqual(created_count, 1)
        self.assertEqual(failed_count, 2)

    @patch(f'{LOGIC_MODULE_PATH}.establish_random_friendships')
    @patch(f'{LOGIC_MODULE_PATH}._create_single_dummy_user')
    @patch(f'{LOGIC_MODULE_PATH}._prepare_dummy_data_config')
    def test_flow_with_zero_users_requested(
        self, mock_prepare_config, mock_create_user, mock_establish_friendships
    ):
        """
        Test the behavior when num_users is 0.
        """
        # --- Action ---
        created_count, failed_count = generate_dummy_users_data(num_users=0, password='pw')

        # --- Assertions ---
        # User creation loop should not run
        mock_create_user.assert_not_called()
        
        # Friendship function should be called with an empty list
        mock_establish_friendships.assert_called_once_with([])
        
        # Final counts should be zero
        self.assertEqual(created_count, 0)
        self.assertEqual(failed_count, 0)