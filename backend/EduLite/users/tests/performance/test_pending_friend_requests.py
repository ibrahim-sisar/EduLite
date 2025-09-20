# users/tests/performance/test_pending_friend_requests_performance.py - Simple Performance Tests
"""
Simple performance tests for PendingFriendRequestListView using DjangoPerformanceAPITestCase.

This file demonstrates how to add performance monitoring to regular Django tests
with just a few assertions for response time, memory usage, and query count.
"""

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient
import json

# Import Mercury performance testing framework
from django_mercury import DjangoPerformanceAPITestCase, monitor_django_view

MERCURY_AVAILABLE = True

from ...models import UserProfile, ProfileFriendRequest
from ..fixtures.test_data_generators import (
    create_students_bulk,
    create_teachers_bulk,
    setup_friend_relationships,
)
from ..fixtures.bulk_test_users import create_bulk_test_users


class PendingFriendRequestsPerformanceTest(DjangoPerformanceAPITestCase):
    """
    Simple performance tests for friend request API endpoints.

    Each test monitors the API call and checks 3 key metrics:
    - Response time (should be fast)
    - Memory usage (should be reasonable)
    - Query count (should be optimized)

    Note: Memory assertions use 150MB threshold to account for:
    - Django framework baseline (~90-100MB)
    - Test database and fixtures
    - Mercury monitoring overhead
    - Python garbage collection delays
    """

    @classmethod
    def setUpTestData(cls):
        """Create all test data once using fixtures."""
        # Create main test user
        cls.test_user = User.objects.create_user(
            username="perf_test_user", email="perf@test.com", password="testpass123"
        )

        # Create bulk users for performance testing (25 users)
        cls.bulk_users = create_bulk_test_users("perf", 25)

        # Create students and teachers using fixtures
        cls.students = create_students_bulk()
        cls.teachers = create_teachers_bulk()

        # Set up some friend relationships
        setup_friend_relationships(cls.students, cls.teachers)

        # Create friend requests TO our test user from bulk users
        cls.incoming_requests = []
        for i, sender in enumerate(cls.bulk_users[:10]):
            request = ProfileFriendRequest.objects.create(
                sender=sender.profile,
                receiver=cls.test_user.profile,
                message=f"Friend request {i}",
            )
            cls.incoming_requests.append(request)

        # Create friend requests FROM our test user to others
        cls.outgoing_requests = []
        for i, receiver in enumerate(cls.bulk_users[10:15]):
            request = ProfileFriendRequest.objects.create(
                sender=cls.test_user.profile,
                receiver=receiver.profile,
                message=f"Outgoing request {i}",
            )
            cls.outgoing_requests.append(request)

    def setUp(self):
        """Set up authenticated client for each test."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_list_pending_requests_performance(self):
        """Test performance of listing pending friend requests."""
        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("list_pending_requests") as monitor:
                response = self.client.get("/api/friend-requests/pending/")

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                len(response.data["results"]), 10
            )  # We have 10 incoming requests

            # Performance assertions - the key part!
            self.assertResponseTimeLess(
                monitor.metrics, 100, "List requests should be fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Should use reasonable memory"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(monitor.metrics, 5, "Should use optimized queries")
        else:
            # Fallback without monitoring
            response = self.client.get("/api/friend-requests/pending/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_friend_request_performance(self):
        """Test performance of sending a friend request."""
        # Use a bulk user that doesn't have a friend request yet
        receiver = self.bulk_users[20]  # Use user at index 20 (no existing requests)

        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("send_friend_request") as monitor:
                response = self.client.post(
                    "/api/friend-requests/send/",
                    data=json.dumps({"receiver_profile_id": receiver.profile.id}),
                    content_type="application/json",
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("request_id", response.data)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 150, "Send request should be fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Should use minimal memory"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(monitor.metrics, 10, "Should minimize queries")
        else:
            response = self.client.post(
                "/api/friend-requests/send/",
                data=json.dumps({"receiver_profile_id": receiver.profile.id}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accept_friend_request_performance(self):
        """Test performance of accepting a friend request."""
        # Use one of the pre-created incoming friend requests
        friend_request = self.incoming_requests[0]

        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("accept_friend_request") as monitor:
                response = self.client.post(
                    f"/api/friend-requests/{friend_request.pk}/accept/"
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Check friendship was created
            self.assertTrue(
                self.test_user.profile.friends.filter(
                    pk=friend_request.sender.user.pk
                ).exists()
            )

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 200, "Accept should be reasonably fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Should use reasonable memory"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(
                monitor.metrics, 10, "Accept involves multiple operations"
            )
        else:
            response = self.client.post(
                f"/api/friend-requests/{friend_request.pk}/accept/"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination_performance(self):
        """Test performance with different page sizes."""
        # We already have 10 incoming requests from setUpTestData

        if MERCURY_AVAILABLE:
            # Test with default pagination (page 1)
            with monitor_django_view("paginated_list") as monitor:
                response = self.client.get("/api/friend-requests/pending/")

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Default page size is 10, so we should get all 10 requests
            self.assertEqual(len(response.data["results"]), 10)
            self.assertEqual(response.data["count"], 10)  # Total incoming requests

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 100, "Pagination should be fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Pagination should limit memory"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(monitor.metrics, 5, "Pagination should be optimized")
        else:
            response = self.client.get("/api/friend-requests/pending/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_empty_results_performance(self):
        """Test performance when user has no friend requests."""
        # Create a new user with no friend requests
        empty_user = User.objects.create_user(
            username="empty_requests_user",
            email="empty@test.com",
            password="testpass123",
        )

        # Use new client for this user
        empty_client = APIClient()
        empty_client.force_authenticate(user=empty_user)

        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("empty_list") as monitor:
                response = empty_client.get("/api/friend-requests/pending/")

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 0)
            self.assertEqual(response.data["count"], 0)

            # Performance assertions - should be very fast with no data
            self.assertResponseTimeLess(
                monitor.metrics, 50, "Empty list should be very fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Empty list should use minimal memory"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(
                monitor.metrics, 3, "Empty list should use minimal queries"
            )
        else:
            response = empty_client.get("/api/friend-requests/pending/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 0)

    def test_different_request_types_performance(self):
        """Test performance of different request type filters."""
        # We already have 10 incoming and 5 outgoing requests from setUpTestData

        if MERCURY_AVAILABLE:
            # Test "sent" filter
            with monitor_django_view("sent_requests") as monitor:
                response = self.client.get("/api/friend-requests/pending/?type=sent")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 5)  # Our outgoing requests

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 100, "Filtered list should be fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Filtered list memory usage"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(
                monitor.metrics, 5, "Filtered list query optimization"
            )

            # Test "all" filter (Note: default page size is 10)
            with monitor_django_view("all_requests") as monitor:
                response = self.client.get("/api/friend-requests/pending/?type=all")

            # With pagination, we'll only get 10 results on first page
            self.assertEqual(len(response.data["results"]), 10)  # Limited by page size
            self.assertEqual(response.data["count"], 15)  # Total count is 15

            # Performance should still be good with more results
            self.assertResponseTimeLess(
                monitor.metrics, 150, "All requests should still be fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "All requests memory usage"
            )  # 150MB accounts for Django baseline
            self.assertQueriesLess(
                monitor.metrics, 5, "All requests should use same queries"
            )
        else:
            response = self.client.get("/api/friend-requests/pending/?type=sent")
            self.assertEqual(response.status_code, status.HTTP_200_OK)


# That's it! Simple, clean performance testing with just the metrics we care about.
