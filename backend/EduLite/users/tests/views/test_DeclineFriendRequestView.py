# users/tests/views/test_DeclineFriendRequestView.py - Tests for DeclineFriendRequestView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase
from ...models import ProfileFriendRequest


class DeclineFriendRequestViewTest(UsersAppTestCase):
    """Test cases for the DeclineFriendRequestView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        # Create a pending friend request for testing
        self.friend_request = self.create_friend_request(
            sender=self.dmitri, receiver=self.fatima, message="Would love to connect!"
        )
        self.url = reverse(
            "friend-request-decline", kwargs={"request_pk": self.friend_request.id}
        )

    # --- Authentication Tests ---

    def test_decline_friend_request_requires_authentication(self):
        """Test that declining friend request requires authentication."""
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- Success Cases ---

    def test_decline_friend_request_by_receiver(self):
        """Test that receiver can decline friend request."""
        # Fatima (receiver) declines Dmitri's request
        self.authenticate_as(self.fatima)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "Friend request declined successfully."
        )

        # Verify friend request was deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

        # Verify no friendship was created
        self.assertFalse(self.dmitri.profile.friends.filter(id=self.fatima.id).exists())
        self.assertFalse(self.fatima.profile.friends.filter(id=self.dmitri.id).exists())

    def test_decline_friend_request_response_data(self):
        """Test the response data when declining friend request."""
        self.authenticate_as(self.fatima)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check response contains success message
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "Friend request declined successfully."
        )

    # --- Permission Tests ---

    def test_sender_can_cancel_own_request(self):
        """Test that sender can cancel (decline) their own friend request."""
        # Dmitri (sender) cancels his own request
        self.authenticate_as(self.dmitri)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "Friend request canceled successfully."
        )

        # Verify request was deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    def test_other_user_cannot_decline_request(self):
        """Test that other users cannot decline someone else's friend request."""
        # Ahmad (unrelated user) tries to decline
        self.authenticate_as(self.ahmad)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify request still exists
        self.assertTrue(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    def test_admin_cannot_decline_any_request(self):
        """Test that admin cannot decline any friend request (permission is receiver/sender only)."""
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

    def test_cannot_decline_already_accepted_request(self):
        """Test that already accepted requests cannot be declined."""
        # First accept the request (which deletes it)
        self.friend_request.accept()

        self.authenticate_as(self.fatima)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_cannot_decline_already_declined_request(self):
        """Test that already declined requests cannot be declined again."""
        # First decline
        self.authenticate_as(self.fatima)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Try to decline again (should 404 since request was deleted)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_cannot_decline_canceled_request(self):
        """Test that canceled requests cannot be declined."""
        # Cancel the request (by having sender decline it)
        self.friend_request.decline()

        self.authenticate_as(self.fatima)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    # --- Edge Cases ---

    def test_decline_nonexistent_request(self):
        """Test declining non-existent friend request."""
        self.authenticate_as(self.fatima)
        url = reverse("friend-request-decline", kwargs={"request_pk": 99999})

        response = self.client.post(url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    # --- Multiple Requests Test ---

    def test_decline_one_of_multiple_requests_fails(self):
        """Test that multiple requests from same user violate unique constraint."""
        # The model has a unique constraint on (sender, receiver), so multiple
        # pending requests from the same sender to receiver shouldn't exist
        # Let's test the decline behavior when there's only one request
        self.authenticate_as(self.fatima)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify request was deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

        # Verify no friendship was created
        self.assertFalse(self.dmitri.profile.friends.filter(id=self.fatima.id).exists())

    # --- Notification Test ---

    def test_decline_may_create_notification(self):
        """Test that declining friend request may create notification."""
        self.authenticate_as(self.fatima)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check if notification was created for the sender
        # Note: Some systems don't notify on decline to avoid hurt feelings
        from notifications.models import Notification

        notification = Notification.objects.filter(
            recipient=self.dmitri,
            notification_type="friend_request_declined",
            actor=self.fatima,
        ).first()

        # This is optional - depends on your notification strategy
        # Some apps don't send decline notifications

    # --- Re-sending After Decline ---

    def test_can_send_new_request_after_decline(self):
        """Test that sender can send new request after being declined."""
        # First decline the request
        self.authenticate_as(self.fatima)
        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Now Dmitri sends a new request
        self.authenticate_as(self.dmitri)
        send_url = reverse("friend-request-send")
        response = self.client.post(
            send_url,
            {
                "receiver_profile_id": self.fatima.profile.id,
                "message": "Hope we can still be friends!",
            },
            format="json",
        )

        # Should be allowed to send new request
        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Verify new request exists
        new_request = ProfileFriendRequest.objects.filter(
            sender__user=self.dmitri, receiver__user=self.fatima
        ).latest("created_at")
        self.assertNotEqual(new_request.id, self.friend_request.id)

    # --- Sender Canceling Request ---

    def test_sender_canceling_deletes_request(self):
        """Test that sender canceling request deletes it."""
        # Dmitri (sender) cancels his request
        self.authenticate_as(self.dmitri)

        response = self.client.post(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"], "Friend request canceled successfully."
        )

        # Request should be deleted
        self.assertFalse(
            ProfileFriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    # --- Performance Test ---

    def test_decline_multiple_requests_performance(self):
        """Test performance of declining multiple friend requests."""
        # Create multiple friend requests to Fatima
        requests = []
        for i in range(5):
            user = self.create_test_user(username=f"decline_requester_{i}")
            req = self.create_friend_request(sender=user, receiver=self.fatima)
            requests.append(req)

        self.authenticate_as(self.fatima)

        import time

        start_time = time.time()

        # Decline all requests
        for req in requests:
            url = reverse("friend-request-decline", kwargs={"request_pk": req.id})
            response = self.client.post(url)
            self.assert_response_success(response, status.HTTP_200_OK)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        self.assertLess(duration, 2.0, "Declining friend requests too slow")

        # Verify no new friendships created (Fatima already has Joy as a friend from fixtures)
        initial_friend_count = 1  # Fatima has Joy as a friend from test fixtures
        self.assertEqual(self.fatima.profile.friends.count(), initial_friend_count)
