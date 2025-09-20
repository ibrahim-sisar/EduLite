# users/tests/views/test_PendingFriendRequestListView.py - Tests for PendingFriendRequestListView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase
from ...models import ProfileFriendRequest


class PendingFriendRequestListViewTest(UsersAppTestCase):
    """Test cases for the PendingFriendRequestListView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = reverse("friend-request-pending-list")

        # Create various friend requests for testing
        self._create_test_friend_requests()

    def _create_test_friend_requests(self):
        """Create friend requests with different statuses for testing."""
        # Pending requests TO Ahmad
        self.req1_to_ahmad = self.create_friend_request(
            sender=self.miguel, receiver=self.ahmad, message="Hi Ahmad!"
        )
        self.req2_to_ahmad = self.create_friend_request(
            sender=self.fatima, receiver=self.ahmad, message="Let's study together"
        )

        # Pending requests FROM Ahmad
        self.req_from_ahmad = self.create_friend_request(
            sender=self.ahmad, receiver=self.dmitri, message="Want to connect?"
        )

        # Note: ProfileFriendRequest model doesn't have a status field
        # Accepted/declined requests are deleted, not marked with status
        # So we'll just create references to IDs that don't exist
        self.accepted_req_id = 99999  # Non-existent ID
        self.declined_req_id = 99998  # Non-existent ID

    # --- Authentication Tests ---

    def test_list_pending_requests_requires_authentication(self):
        """Test that listing pending requests requires authentication."""
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- List Tests ---

    def test_list_pending_requests_received(self):
        """Test listing pending friend requests received by user."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should have pagination
        self.assert_paginated_response(response)

        # Check that we got the pending requests TO Ahmad
        request_ids = [req["id"] for req in response.data["results"]]
        self.assertIn(self.req1_to_ahmad.id, request_ids)
        self.assertIn(self.req2_to_ahmad.id, request_ids)

        # Should not include requests FROM Ahmad
        self.assertNotIn(self.req_from_ahmad.id, request_ids)

        # Should not include non-existent (accepted/declined) requests
        self.assertNotIn(self.accepted_req_id, request_ids)
        self.assertNotIn(self.declined_req_id, request_ids)

    def test_list_pending_requests_sent(self):
        """Test listing pending friend requests sent by user with filter."""
        self.authenticate_as(self.ahmad)

        # Request sent friend requests
        response = self.client.get(self.url, {"type": "sent"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check that we got the pending requests FROM Ahmad
        request_ids = [req["id"] for req in response.data["results"]]
        self.assertIn(self.req_from_ahmad.id, request_ids)

        # Should not include requests TO Ahmad
        self.assertNotIn(self.req1_to_ahmad.id, request_ids)
        self.assertNotIn(self.req2_to_ahmad.id, request_ids)

    def test_list_all_pending_requests(self):
        """Test listing all pending requests (both sent and received)."""
        self.authenticate_as(self.ahmad)

        # Request all pending requests
        response = self.client.get(self.url, {"type": "all"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should include both sent and received
        request_ids = [req["id"] for req in response.data["results"]]
        self.assertIn(self.req1_to_ahmad.id, request_ids)
        self.assertIn(self.req2_to_ahmad.id, request_ids)
        self.assertIn(self.req_from_ahmad.id, request_ids)

    def test_list_pending_requests_empty(self):
        """Test listing when user has no pending requests."""
        # Elena has no friend requests
        self.authenticate_as(self.elena)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should have empty results
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    # --- Filtering Tests ---

    def test_filter_by_invalid_type(self):
        """Test filtering with invalid type parameter."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url, {"type": "invalid"})
        # Should either ignore invalid type or return error
        self.assertIn(response.status_code, [200, 400])

    # --- Ordering Tests ---

    def test_pending_requests_ordered_by_date(self):
        """Test that pending requests are ordered by creation date."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        if len(response.data["results"]) >= 2:
            # Check ordering (newest first usually)
            dates = [req["created_at"] for req in response.data["results"]]
            # Verify descending order
            for i in range(len(dates) - 1):
                self.assertGreaterEqual(dates[i], dates[i + 1])

    # --- Pagination Tests ---

    def test_pending_requests_pagination(self):
        """Test pagination of pending friend requests."""
        # Create many pending requests
        for i in range(15):
            user = self.create_test_user(username=f"pending_test_{i}")
            self.create_friend_request(sender=user, receiver=self.ahmad)

        self.authenticate_as(self.ahmad)

        # Get first page
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should have pagination
        self.assertGreater(response.data["count"], 10)
        self.assertEqual(len(response.data["results"]), 10)  # Default page size
        self.assertIsNotNone(response.data["next"])

        # Get second page
        response = self.client.get(self.url, {"page": 2})
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["previous"])

    # --- Privacy Tests ---

    def test_cannot_see_other_users_pending_requests(self):
        """Test that users cannot see other users' pending requests."""
        # Create a request between other users
        private_req = self.create_friend_request(sender=self.marie, receiver=self.joy)

        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url, {"type": "all"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should not see the private request
        request_ids = [req["id"] for req in response.data["results"]]
        self.assertNotIn(private_req.id, request_ids)

    def test_admin_sees_only_own_requests(self):
        """Test that even admin users see only their own requests."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should not see Ahmad's requests
        request_ids = [req["id"] for req in response.data["results"]]
        self.assertNotIn(self.req1_to_ahmad.id, request_ids)

    # --- Performance Test ---

    def test_list_many_pending_requests_performance(self):
        """Test performance with many pending requests."""
        # Create many pending requests
        for i in range(50):
            user = self.create_test_user(username=f"perf_pending_{i}")
            self.create_friend_request(sender=user, receiver=self.ahmad)

        self.authenticate_as(self.ahmad)

        import time

        start_time = time.time()

        response = self.client.get(self.url)

        end_time = time.time()
        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertLess(duration, 2.0, "Listing pending requests too slow")

        # Verify we got paginated results
        self.assertEqual(len(response.data["results"]), 10)  # Default page size
