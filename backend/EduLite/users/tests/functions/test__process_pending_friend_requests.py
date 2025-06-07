# users/tests/functions/test__process_pending_friend_requests.py

from django.test import TestCase
from unittest.mock import patch, MagicMock

from ...management.logic import _process_pending_friend_requests

LOGIC_MODULE_PATH = 'users.management.logic'

class ProcessPendingFriendRequestsTests(TestCase):
    """
    Test suite for the _process_pending_friend_requests helper function.
    """

    def setUp(self):
        """
        Create a list of mock friend request objects for testing.
        Each mock needs .accept() and .decline() methods and mock user attributes for print statements.
        """
        self.mock_requests = []
        for i in range(5):
            mock_request = MagicMock()
            mock_request.sender.user.username = f'sender{i}'
            mock_request.receiver.user.username = f'receiver{i}'
            # The accept and decline methods will also be mocks that we can track calls on
            self.mock_requests.append(mock_request)

    def test_handles_empty_request_list(self):
        """
        Test that the function handles an empty list of requests gracefully.
        """
        result = _process_pending_friend_requests([])
        
        # It should return zero counts for both
        self.assertEqual(result, {'accepted_count': 0, 'declined_count': 0})

    @patch(f'{LOGIC_MODULE_PATH}.random.choice')
    def test_all_requests_are_accepted(self, mock_random_choice):
        """
        Test the scenario where all pending requests are accepted.
        """
        # --- Setup Mock ---
        # Make random.choice always return True for the 'accept' check
        mock_random_choice.return_value = True

        # --- Action ---
        stats = _process_pending_friend_requests(self.mock_requests)

        # --- Assertions ---
        # Verify each request's .accept() method was called once
        for req in self.mock_requests:
            req.accept.assert_called_once()
            req.decline.assert_not_called()

        # Verify the final statistics are correct
        self.assertEqual(stats, {'accepted_count': 5, 'declined_count': 0})

    @patch(f'{LOGIC_MODULE_PATH}.random.choice')
    def test_all_requests_are_declined(self, mock_random_choice):
        """
        Test the scenario where all pending requests are declined.
        """
        # --- Setup Mock ---
        # Make random.choice return False for the 'accept' check, and True for the 'decline' check
        mock_random_choice.side_effect = [
            False, True,  # Request 1: Not accepted, is declined
            False, True,  # Request 2: Not accepted, is declined
            False, True,  # Request 3: Not accepted, is declined
            False, True,  # Request 4: Not accepted, is declined
            False, True,  # Request 5: Not accepted, is declined
        ]

        # --- Action ---
        stats = _process_pending_friend_requests(self.mock_requests)

        # --- Assertions ---
        # Verify each request's .decline() method was called once
        for req in self.mock_requests:
            req.accept.assert_not_called()
            req.decline.assert_called_once()

        # Verify the final statistics are correct (This will fail until you fix the return statement)
        self.assertEqual(stats, {'accepted_count': 0, 'declined_count': 5})
        
    @patch(f'{LOGIC_MODULE_PATH}.random.choice')
    def test_all_requests_are_ignored(self, mock_random_choice):
        """
        Test the scenario where all pending requests are ignored.
        """
        # --- Setup Mock ---
        # Make random.choice always return False for both checks
        mock_random_choice.return_value = False
        
        # --- Action ---
        stats = _process_pending_friend_requests(self.mock_requests)

        # --- Assertions ---
        # Verify neither accept() nor decline() was called
        for req in self.mock_requests:
            req.accept.assert_not_called()
            req.decline.assert_not_called()
        
        # Verify the final statistics are correct
        self.assertEqual(stats, {'accepted_count': 0, 'declined_count': 0})

    @patch(f'{LOGIC_MODULE_PATH}.random.choice')
    def test_mixed_outcomes(self, mock_random_choice):
        """
        Test a mixed scenario of accept, decline, and ignore actions.
        """
        # --- Setup Mock ---
        # Define a specific sequence of random choices
        mock_random_choice.side_effect = [
            True,           # Request 1: Accept
            False, True,    # Request 2: Decline
            False, False,   # Request 3: Ignore
            True,           # Request 4: Accept
            False, True,    # Request 5: Decline
        ]
        
        # --- Action ---
        stats = _process_pending_friend_requests(self.mock_requests)
        
        # --- Assertions ---
        # Check calls for each mock request individually
        self.mock_requests[0].accept.assert_called_once()
        self.mock_requests[0].decline.assert_not_called()

        self.mock_requests[1].accept.assert_not_called()
        self.mock_requests[1].decline.assert_called_once()

        self.mock_requests[2].accept.assert_not_called()
        self.mock_requests[2].decline.assert_not_called()

        self.mock_requests[3].accept.assert_called_once()
        self.mock_requests[3].decline.assert_not_called()

        self.mock_requests[4].accept.assert_not_called()
        self.mock_requests[4].decline.assert_called_once()
        
        # Verify the final statistics are correct (This will also fail until you fix the return statement)
        self.assertEqual(stats, {'accepted_count': 2, 'declined_count': 2})