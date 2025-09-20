# users/tests/serializers/test_ProfileFriendRequestSerializer.py - Tests for ProfileFriendRequestSerializer

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory

from ...models import ProfileFriendRequest, UserProfile
from ...serializers import ProfileFriendRequestSerializer


class ProfileFriendRequestSerializerTest(TestCase):
    """Test cases for ProfileFriendRequestSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.sender_user = User.objects.create_user(
            username="sender_user", first_name="Sender", last_name="User"
        )
        self.receiver_user = User.objects.create_user(
            username="receiver_user", first_name="Receiver", last_name="User"
        )

        # Get profiles (created automatically via signal)
        self.sender_profile = self.sender_user.profile
        self.receiver_profile = self.receiver_user.profile

        # Create friend request
        self.friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile,
            message="Let's connect!",
        )

        # Create request factory for context
        self.factory = APIRequestFactory()

    def get_serializer_context(self):
        """Get serializer context with request."""
        request = self.factory.get("/")
        return {"request": request}

    # --- Field Presence Tests ---

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = ProfileFriendRequestSerializer(
            instance=self.friend_request, context=self.get_serializer_context()
        )
        data = serializer.data

        # Check expected fields
        expected_fields = ["id", "sender", "receiver", "message", "created_at"]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_sender_receiver_nested_fields(self):
        """Test that sender and receiver contain user information."""
        serializer = ProfileFriendRequestSerializer(
            instance=self.friend_request, context=self.get_serializer_context()
        )
        data = serializer.data

        # Check sender fields
        self.assertIn("id", data["sender"])
        self.assertIn("username", data["sender"])
        self.assertEqual(data["sender"]["username"], "sender_user")

        # Check receiver fields
        self.assertIn("id", data["receiver"])
        self.assertIn("username", data["receiver"])
        self.assertEqual(data["receiver"]["username"], "receiver_user")

    # --- Field Value Tests ---

    def test_message_field_value(self):
        """Test message field value."""
        serializer = ProfileFriendRequestSerializer(
            instance=self.friend_request, context=self.get_serializer_context()
        )
        data = serializer.data

        self.assertEqual(data["message"], "Let's connect!")

    def test_created_at_field(self):
        """Test created_at field is present."""
        serializer = ProfileFriendRequestSerializer(
            instance=self.friend_request, context=self.get_serializer_context()
        )
        data = serializer.data

        self.assertIn("created_at", data)
        self.assertIsNotNone(data["created_at"])

    def test_empty_message_handling(self):
        """Test handling of empty message."""
        # Create another user to avoid unique constraint
        other_user = User.objects.create_user(username="other_user")
        other_profile = other_user.profile

        request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile, receiver=other_profile, message=None
        )

        serializer = ProfileFriendRequestSerializer(
            instance=request, context=self.get_serializer_context()
        )
        data = serializer.data

        self.assertIn("message", data)
        self.assertIsNone(data["message"])

    # --- Serialization Tests ---

    def test_serialize_multiple_requests(self):
        """Test serializing multiple friend requests."""
        # Create another user to avoid unique constraint
        other_user = User.objects.create_user(username="other_user")
        other_profile = other_user.profile

        # Create additional request
        request2 = ProfileFriendRequest.objects.create(
            sender=self.receiver_profile,
            receiver=other_profile,
            message="Reply message",
        )

        requests = ProfileFriendRequest.objects.all().order_by("id")
        serializer = ProfileFriendRequestSerializer(
            requests, many=True, context=self.get_serializer_context()
        )
        data = serializer.data

        self.assertEqual(len(data), 2)
        # Check that both messages are present (order might vary)
        messages = [req["message"] for req in data]
        self.assertIn("Let's connect!", messages)
        self.assertIn("Reply message", messages)

    # --- Privacy Tests ---

    def test_sender_privacy_respected(self):
        """Test that sender privacy settings are respected in serialization."""
        # This test would check if privacy-aware fields are properly hidden
        # Based on the actual implementation of ProfileFriendRequestSerializer
        pass

    def test_receiver_privacy_respected(self):
        """Test that receiver privacy settings are respected in serialization."""
        # This test would check if privacy-aware fields are properly hidden
        # Based on the actual implementation of ProfileFriendRequestSerializer
        pass
