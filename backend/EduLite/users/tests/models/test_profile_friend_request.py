# users/tests/models/test_profile_friend_request.py - Tests for ProfileFriendRequest model

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from ...models import UserProfile, ProfileFriendRequest
from .. import UsersModelTestCase


class ProfileFriendRequestModelTest(UsersModelTestCase):
    """Test cases for the ProfileFriendRequest model."""

    def setUp(self):
        """Set up test users."""
        super().setUp()
        self.user1 = self.create_test_user(username="user1")
        self.user2 = self.create_test_user(username="user2")
        self.user3 = self.create_test_user(username="user3")

    def test_friend_request_creation(self):
        """Test creating a valid friend request."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile,
            receiver=self.user2.profile,
            message="Let's be friends!",
        )

        self.assertEqual(request.sender, self.user1.profile)
        self.assertEqual(request.receiver, self.user2.profile)
        self.assertEqual(request.message, "Let's be friends!")
        self.assertIsNotNone(request.created_at)

    def test_friend_request_str_representation(self):
        """Test string representation of friend request."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        expected = f"Friend request from {self.user1.username} to {self.user2.username}"
        self.assertEqual(str(request), expected)

    def test_friend_request_ordering(self):
        """Test that friend requests are ordered by created_at descending."""
        # Create requests with time gaps
        request1 = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        request2 = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user3.profile
        )

        # Most recent should be first
        requests = ProfileFriendRequest.objects.all()
        self.assertEqual(requests[0], request2)
        self.assertEqual(requests[1], request1)

    def test_friend_request_to_self_validation(self):
        """Test that users cannot send friend requests to themselves."""
        request = ProfileFriendRequest(
            sender=self.user1.profile, receiver=self.user1.profile
        )

        with self.assertRaises(ValidationError) as context:
            request.full_clean()

        self.assertIn("Cannot send a friend request to oneself", str(context.exception))

    def test_friend_request_to_existing_friend_validation(self):
        """Test that users cannot send friend requests to existing friends."""
        # Make them friends
        self.user1.profile.friends.add(self.user2)

        request = ProfileFriendRequest(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        with self.assertRaises(ValidationError) as context:
            request.full_clean()

        self.assertIn(
            "Cannot send a friend request to a friend", str(context.exception)
        )

    def test_friend_request_reverse_friendship_validation(self):
        """Test validation when receiver already has sender as friend."""
        # Make user2 have user1 as friend (but not vice versa)
        self.user2.profile.friends.add(self.user1)

        request = ProfileFriendRequest(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        with self.assertRaises(ValidationError) as context:
            request.full_clean()

        self.assertIn(
            "Cannot send a friend request to a friend", str(context.exception)
        )

    def test_friend_request_unique_constraint(self):
        """Test that duplicate friend requests are prevented."""
        # Create first request
        ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Try to create duplicate
        with self.assertRaises(IntegrityError):
            ProfileFriendRequest.objects.create(
                sender=self.user1.profile, receiver=self.user2.profile
            )

    def test_friend_request_accept(self):
        """Test accepting a friend request."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Accept the request
        result = request.accept()

        # Check result
        self.assertTrue(result)

        # Check that users are now friends
        self.assertIn(self.user2, self.user1.profile.friends.all())
        self.assertIn(self.user1, self.user2.profile.friends.all())

        # Check that request is deleted
        self.assertFalse(ProfileFriendRequest.objects.filter(id=request.id).exists())

    def test_friend_request_accept_idempotent(self):
        """Test that accepting an already accepted request returns False."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Accept once
        request.accept()

        # Try to accept again (request no longer exists)
        result = request.accept()
        self.assertFalse(result)

    def test_friend_request_decline(self):
        """Test declining a friend request."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Decline the request
        result = request.decline()

        # Check result
        self.assertTrue(result)

        # Check that users are not friends
        self.assertNotIn(self.user2, self.user1.profile.friends.all())
        self.assertNotIn(self.user1, self.user2.profile.friends.all())

        # Check that request is deleted
        self.assertFalse(ProfileFriendRequest.objects.filter(id=request.id).exists())

    def test_friend_request_decline_idempotent(self):
        """Test that declining an already declined request returns False."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Decline once
        request.decline()

        # Try to decline again
        result = request.decline()
        self.assertFalse(result)

    def test_friend_request_accept_race_condition_protection(self):
        """Test that accept() is protected against race conditions."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Simulate the request being deleted by another process
        ProfileFriendRequest.objects.filter(id=request.id).delete()

        # Try to accept - should return False gracefully
        result = request.accept()
        self.assertFalse(result)

    def test_friend_request_decline_race_condition_protection(self):
        """Test that decline() is protected against race conditions."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )

        # Simulate the request being deleted by another process
        ProfileFriendRequest.objects.filter(id=request.id).delete()

        # Try to decline - should return False gracefully
        result = request.decline()
        self.assertFalse(result)

    def test_friend_request_cascade_delete_sender(self):
        """Test that friend requests are deleted when sender is deleted."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )
        request_id = request.id

        # Delete sender
        self.user1.delete()

        # Check that request is deleted
        self.assertFalse(ProfileFriendRequest.objects.filter(id=request_id).exists())

    def test_friend_request_cascade_delete_receiver(self):
        """Test that friend requests are deleted when receiver is deleted."""
        request = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile
        )
        request_id = request.id

        # Delete receiver
        self.user2.delete()

        # Check that request is deleted
        self.assertFalse(ProfileFriendRequest.objects.filter(id=request_id).exists())

    def test_friend_request_message_optional(self):
        """Test that message field is optional."""
        # With message
        request1 = ProfileFriendRequest.objects.create(
            sender=self.user1.profile, receiver=self.user2.profile, message="Hi there!"
        )
        self.assertEqual(request1.message, "Hi there!")

        # Without message (null=True means default is None)
        request2 = ProfileFriendRequest.objects.create(
            sender=self.user2.profile, receiver=self.user3.profile
        )
        self.assertIsNone(request2.message)

    def test_friend_request_message_max_length(self):
        """Test message field max length constraint."""
        # Valid message length
        request = ProfileFriendRequest(
            sender=self.user1.profile, receiver=self.user2.profile, message="A" * 500
        )
        request.full_clean()  # Should not raise
        request.save()

        # Note: Django's TextField doesn't enforce max_length at model validation
        # It's only enforced in forms. This is standard Django behavior.
        request.message = "A" * 501
        request.full_clean()  # This will NOT raise for TextField
        request.save()  # This should work

        # The max_length on TextField is for form field generation
        self.assertEqual(len(request.message), 501)
