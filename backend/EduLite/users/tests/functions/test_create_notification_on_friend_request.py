# users/tests/functions/test_create_notification_on_friend_request.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from ...models import UserProfile, ProfileFriendRequest
from ...signals import create_notification_on_friend_request

User = get_user_model()


class CreateNotificationOnFriendRequestTests(TestCase):
    """
    Test suite for the create_notification_on_friend_request signal handler.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data that will be used across multiple test methods.
        """
        # Create test users
        cls.sender_user = User.objects.create_user(
            username="sender", password="password123"
        )
        cls.receiver_user = User.objects.create_user(
            username="receiver", password="password123"
        )

        # Get their profiles (created automatically by signals)
        cls.sender_profile = UserProfile.objects.get(user=cls.sender_user)
        cls.receiver_profile = UserProfile.objects.get(user=cls.receiver_user)

    @patch("notifications.models.Notification")
    def test_creates_notification_on_friend_request_creation(self, mock_notification_model):
        """
        Test that the signal handler creates a notification when a new friend request is created.
        """
        # --- Setup Mock ---
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.create.return_value = mock_notification_instance

        # --- Action ---
        # Create a friend request, which should trigger the signal
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # --- Assertions ---
        # Verify that Notification.objects.create was called exactly once
        mock_notification_model.objects.create.assert_called_once_with(
            recipient=self.receiver_user,
            actor=self.sender_user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
            target=friend_request,
            description="",
        )

    @patch("notifications.models.Notification")
    def test_does_not_create_notification_on_friend_request_update(self, mock_notification_model):
        """
        Test that the signal handler does not create a notification when an existing friend request is updated.
        """
        # --- Setup ---
        # First create a friend request
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # Reset the mock to clear any calls from the creation above
        mock_notification_model.reset_mock()

        # --- Action ---
        # Update the friend request (this should NOT trigger notification creation)
        friend_request.save()

        # --- Assertions ---
        # Verify that no notification was created during the update
        mock_notification_model.objects.create.assert_not_called()

    @patch("notifications.models.Notification")
    def test_signal_handler_called_with_correct_parameters(self, mock_notification_model):
        """
        Test that the signal handler receives the correct parameters from Django's signal system.
        """
        # --- Setup Mock ---
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.create.return_value = mock_notification_instance

        # --- Action ---
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # --- Assertions ---
        # Verify the notification was created with correct recipient (receiver of friend request)
        call_args = mock_notification_model.objects.create.call_args
        self.assertEqual(call_args.kwargs['recipient'], self.receiver_user)

        # Verify the notification was created with correct actor (sender of friend request)
        self.assertEqual(call_args.kwargs['actor'], self.sender_user)

        # Verify the notification has the correct verb
        self.assertEqual(call_args.kwargs['verb'], "sent you a friend request")

        # Verify the notification has the correct type
        self.assertEqual(call_args.kwargs['notification_type'], "FRIEND_REQUEST")

        # Verify the notification is linked to the friend request via generic foreign key
        self.assertEqual(call_args.kwargs['target'], friend_request)

    def test_signal_handler_function_exists_and_is_callable(self):
        """
        Test that the signal handler function exists and can be called directly.
        """
        # --- Assertions ---
        # Verify the function exists
        self.assertTrue(callable(create_notification_on_friend_request))

        # Verify the function has the expected parameters
        import inspect
        sig = inspect.signature(create_notification_on_friend_request)
        expected_params = ['sender', 'instance', 'created']

        # Check that all expected parameters are present (kwargs is also expected)
        actual_params = list(sig.parameters.keys())
        for param in expected_params:
            self.assertIn(param, actual_params)

    @patch("notifications.models.Notification")
    def test_handles_notification_creation_failure_gracefully(self, mock_notification_model):
        """
        Test that the signal handler handles potential failures in notification creation gracefully.
        The signal handler should catch exceptions and log them without breaking the friend request creation.
        """
        # --- Setup Mock ---
        # Make the notification creation raise an exception
        mock_notification_model.objects.create.side_effect = Exception("Database error")

        # --- Action ---
        # Creating a friend request should still succeed even if notification creation fails
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # --- Assertions ---
        # Verify that the friend request was created successfully despite notification failure
        self.assertIsNotNone(friend_request.id)
        self.assertEqual(friend_request.sender, self.sender_profile)
        self.assertEqual(friend_request.receiver, self.receiver_profile)

        # Verify that the notification creation was attempted
        mock_notification_model.objects.create.assert_called_once()

    @patch("users.signals.logger")
    @patch("notifications.models.Notification")
    def test_logs_notification_creation_failure(self, mock_notification_model, mock_logger):
        """
        Test that the signal handler properly logs notification creation failures.
        """
        # --- Setup Mock ---
        error_message = "Database connection failed"
        mock_notification_model.objects.create.side_effect = Exception(error_message)

        # --- Action ---
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # --- Assertions ---
        # Verify that an error was logged
        mock_logger.error.assert_called_once()

        # Verify the error log contains relevant information (parameterized logging)
        log_call_args = mock_logger.error.call_args[0]
        self.assertIn("Failed to create notification for friend request", log_call_args[0])
        self.assertEqual(log_call_args[1], friend_request.id)  # %s parameter
        self.assertEqual(str(log_call_args[2]), error_message)  # Exception parameter

    @patch("users.signals.logger")
    @patch("notifications.models.Notification")
    def test_logs_successful_notification_creation(self, mock_notification_model, mock_logger):
        """
        Test that the signal handler logs successful notification creation in debug mode.
        """
        # --- Setup Mock ---
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.create.return_value = mock_notification_instance
        mock_logger.isEnabledFor.return_value = True

        # --- Action ---
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # --- Assertions ---
        # Verify that debug logging was called
        mock_logger.debug.assert_called_once()

        # Verify the debug log contains relevant information (parameterized logging)
        debug_call_args = mock_logger.debug.call_args[0]
        self.assertIn("Notification created for friend request", debug_call_args[0])
        self.assertEqual(debug_call_args[1], friend_request.id)        # friend request ID
        self.assertEqual(debug_call_args[2], self.sender_user.username)    # sender username
        self.assertEqual(debug_call_args[3], self.receiver_user.username)  # receiver username

    @patch("notifications.models.Notification")
    def test_notification_links_correct_user_relationships(self, mock_notification_model):
        """
        Test that the notification correctly links the User instances, not the UserProfile instances.
        """
        # --- Setup Mock ---
        mock_notification_instance = MagicMock()
        mock_notification_model.objects.create.return_value = mock_notification_instance

        # --- Action ---
        friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile
        )

        # --- Assertions ---
        call_args = mock_notification_model.objects.create.call_args

        # Verify that User instances are passed, not UserProfile instances
        self.assertIsInstance(call_args.kwargs['recipient'], User)
        self.assertIsInstance(call_args.kwargs['actor'], User)

        # Verify the correct User instances are used
        self.assertEqual(call_args.kwargs['recipient'].username, "receiver")
        self.assertEqual(call_args.kwargs['actor'].username, "sender")
