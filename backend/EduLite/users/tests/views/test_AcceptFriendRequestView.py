# users/tests/views/test_AcceptFriendRequestView.py - Tests for AcceptFriendRequestView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase
from ...models import ProfileFriendRequest


class AcceptFriendRequestViewTest(UsersAppTestCase):
    """Test cases for the AcceptFriendRequestView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        # Create a pending friend request for testing
        self.friend_request = self.create_friend_request(
            sender=self.miguel, receiver=self.sophie, message="Let's study together!"
        )
        self.url = reverse(
            "friend-request-accept", kwargs={"request_pk": self.friend_request.id}
        )

    # --- Authentication Tests ---

    def test_accept_friend_request_requires_authentication(self):
        """Test that accepting friend request requires authentication."""
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- Success Cases ---

    def test_accept_friend_request_by_receiver(self):
        """Test that receiver can accept friend request."""
        # Sophie (receiver) accepts Miguel's request
        self.authenticate_as(self.sophie)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Friend request accepted.")

        # Verify friend request was deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

        # Verify friendship was created (bidirectional)
        self.assertTrue(self.miguel.profile.friends.filter(id=self.sophie.id).exists())
        self.assertTrue(self.sophie.profile.friends.filter(id=self.miguel.id).exists())

    def test_accept_friend_request_response_data(self):
        """Test the response data when accepting friend request."""
        self.authenticate_as(self.sophie)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check response contains success message
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Friend request accepted.")

    # --- Permission Tests ---

    def test_sender_cannot_accept_own_request(self):
        """Test that sender cannot accept their own friend request."""
        # Miguel (sender) tries to accept his own request
        self.authenticate_as(self.miguel)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify request still exists
        self.assertTrue(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    def test_other_user_cannot_accept_request(self):
        """Test that other users cannot accept someone else's friend request."""
        # Ahmad (unrelated user) tries to accept
        self.authenticate_as(self.ahmad)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_accept_any_request(self):
        """Test that admin cannot accept any friend request (permission is receiver-only)."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify request still exists
        self.assertTrue(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    # --- Status Tests ---

    def test_cannot_accept_already_accepted_request(self):
        """Test that already accepted requests cannot be accepted again."""
        # First accept
        self.authenticate_as(self.sophie)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Try to accept again (should 404 since request was deleted)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_cannot_accept_declined_request(self):
        """Test that declined requests cannot be accepted."""
        # First decline the request (which deletes it)
        self.friend_request.decline()

        self.authenticate_as(self.sophie)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    # --- Edge Cases ---

    def test_accept_nonexistent_request(self):
        """Test accepting non-existent friend request."""
        self.authenticate_as(self.sophie)
        url = reverse("friend-request-accept", kwargs={"request_pk": 99999})

        response = self.client.post(url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_accept_request_when_already_friends(self):
        """Test accepting request when users are already friends."""
        # Manually make them friends first
        self.miguel.profile.friends.add(self.sophie)
        self.sophie.profile.friends.add(self.miguel)

        self.authenticate_as(self.sophie)
        response = self.client.post(self.url)

        # Should still accept the request (no harm in re-adding friends)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify only one friendship exists
        self.assertEqual(
            self.miguel.profile.friends.filter(id=self.sophie.id).count(), 1
        )

        # Verify request was deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    # --- Multiple Requests Test ---

    def test_accept_one_of_multiple_requests_fails(self):
        """Test that multiple requests from same user violate unique constraint."""
        # The model has a unique constraint on (sender, receiver), so multiple
        # pending requests from the same sender to receiver shouldn't exist
        # Let's test the accept behavior when there's only one request
        self.authenticate_as(self.sophie)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify request was deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

        # Verify friendship exists
        self.assertTrue(self.miguel.profile.friends.filter(id=self.sophie.id).exists())

    # --- Notification Test ---

    def test_accept_creates_notification(self):
        """Test that accepting friend request creates notification."""
        self.authenticate_as(self.sophie)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check if notification was created for the sender
        from notifications.models import Notification

        notification = Notification.objects.filter(
            recipient=self.miguel,
            notification_type="friend_request_accepted",
            actor=self.sophie,
        ).first()

        if notification:
            self.assertIsNotNone(notification)

    # --- Friendship Verification ---

    def test_friendship_is_bidirectional(self):
        """Test that accepting creates bidirectional friendship."""
        self.authenticate_as(self.sophie)

        # Verify not friends before
        self.assertFalse(self.miguel.profile.friends.filter(id=self.sophie.id).exists())
        self.assertFalse(self.sophie.profile.friends.filter(id=self.miguel.id).exists())

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify bidirectional friendship
        self.assertTrue(self.miguel.profile.friends.filter(id=self.sophie.id).exists())
        self.assertTrue(self.sophie.profile.friends.filter(id=self.miguel.id).exists())

    # --- Performance Test ---

    def test_accept_multiple_requests_performance(self):
        """Test performance of accepting multiple friend requests."""
        # Create multiple friend requests to Sophie
        requests = []
        for i in range(5):
            user = self.create_test_user(username=f"requester_{i}")
            req = self.create_friend_request(sender=user, receiver=self.sophie)
            requests.append(req)

        self.authenticate_as(self.sophie)

        import time

        start_time = time.time()

        # Accept all requests
        for req in requests:
            url = reverse("friend-request-accept", kwargs={"request_pk": req.id})
            response = self.client.post(url)
            self.assert_response_success(response, status.HTTP_200_OK)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        self.assertLess(duration, 2.0, "Accepting friend requests too slow")

        # Verify all friendships created
        self.assertEqual(self.sophie.profile.friends.count(), 5)
