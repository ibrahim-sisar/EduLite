# users/tests/functions/test_establish_random_friendships.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from ...management.logic import establish_random_friendships

User = get_user_model()

LOGIC_MODULE_PATH = 'users.management.logic'


class EstablishRandomFriendshipsTests(TestCase):
    """
    Test suite for the establish_random_friendships orchestrator function.
    """

    def setUp(self):
        """Create a list of mock User objects for use in tests."""
        self.mock_users = [MagicMock(spec=User) for _ in range(5)]

    @patch(f'{LOGIC_MODULE_PATH}._process_pending_friend_requests')
    @patch(f'{LOGIC_MODULE_PATH}._create_pending_friend_requests')
    def test_orchestration_flow_with_enough_users(
        self, mock_create_requests, mock_process_requests
    ):
        """
        Test the main orchestration flow, ensuring helpers are called in sequence.
        """
        # --- Setup Mocks ---
        # Define what the helper functions should return when called
        mock_pending_requests = [MagicMock(), MagicMock()] # A dummy list of request objects
        mock_create_requests.return_value = mock_pending_requests
        
        mock_stats = {'accepted_count': 1, 'declined_count': 1}
        mock_process_requests.return_value = mock_stats

        # --- Action ---
        establish_random_friendships(self.mock_users)

        # --- Assertions ---
        # 1. Verify that the first helper was called once with the list of users
        mock_create_requests.assert_called_once_with(self.mock_users)
        
        # 2. Verify that the second helper was called once with the result from the first helper
        mock_process_requests.assert_called_once_with(mock_pending_requests)

    @patch(f'{LOGIC_MODULE_PATH}._process_pending_friend_requests')
    @patch(f'{LOGIC_MODULE_PATH}._create_pending_friend_requests')
    def test_returns_early_if_user_list_is_too_small(
        self, mock_create_requests, mock_process_requests
    ):
        """
        Test that the function exits early and does not call helpers
        if the list of users has fewer than two people.
        """
        # --- Action & Assertions for a list with one user ---
        establish_random_friendships([self.mock_users[0]])
        mock_create_requests.assert_not_called()
        mock_process_requests.assert_not_called()
        
        # Reset mocks to test the next scenario
        mock_create_requests.reset_mock()
        mock_process_requests.reset_mock()
        
        # --- Action & Assertions for an empty list ---
        establish_random_friendships([])
        mock_create_requests.assert_not_called()
        mock_process_requests.assert_not_called()

    @patch(f'{LOGIC_MODULE_PATH}._process_pending_friend_requests')
    @patch(f'{LOGIC_MODULE_PATH}._create_pending_friend_requests')
    def test_flow_when_no_requests_are_created(
        self, mock_create_requests, mock_process_requests
    ):
        """
        Test that the second helper is called with an empty list if no requests are created.
        """
        # --- Setup Mocks ---
        # Simulate the case where _create_pending_friend_requests runs but creates nothing
        mock_create_requests.return_value = [] # Return an empty list
        mock_process_requests.return_value = {'accepted_count': 0, 'declined_count': 0}

        # --- Action ---
        establish_random_friendships(self.mock_users)
        
        # --- Assertions ---
        # 1. Verify that the creation helper was called
        mock_create_requests.assert_called_once_with(self.mock_users)
        
        # 2. Verify that the processing helper was still called, but with an empty list
        mock_process_requests.assert_called_once_with([])