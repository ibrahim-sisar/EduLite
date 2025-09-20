# users/tests/performance/test_user_profile_performance.py - Performance tests for UserProfile views
"""
Performance testing for UserProfile related views using DjangoPerformanceAPITestCase.

Target View: UserProfileRetrieveUpdateView
Key Performance Metrics:
- Response time: < 150ms for profile retrieval
- Query count: < 10 queries (optimized with select_related/prefetch_related)
- Memory usage: < 150MB (Django baseline + reasonable overhead)

Note: Memory threshold of 150MB accounts for Django framework baseline (~90-100MB),
test database, Mercury monitoring overhead, and Python garbage collection delays.
"""

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient
import json

# Import Mercury performance testing framework
from django_mercury import DjangoPerformanceAPITestCase, monitor_django_view

MERCURY_AVAILABLE = True

from ...models import UserProfile


class UserProfilePerformanceTest(DjangoPerformanceAPITestCase):
    """
    Performance tests for UserProfile API endpoints using DjangoPerformanceAPITestCase.

    Each test monitors the API call and checks 3 key metrics:
    - Response time (should be fast)
    - Memory usage (should be reasonable)
    - Query count (should be optimized)

    These tests verify that profile operations remain performant even with many friends
    and that N+1 queries are avoided through proper use of select_related/prefetch_related.
    """

    @classmethod
    def setUpTestData(cls):
        """Create all test data once using fixtures."""
        # Create main test user with profile
        cls.test_user = User.objects.create_user(
            username="profile_test_main",
            email="main@profile.test",
            first_name="Main",
            last_name="User",
        )

        # Create multiple friend users
        cls.friend_users = []
        for i in range(20):  # Create 20 friends to test performance with relationships
            friend = User.objects.create_user(
                username=f"profile_test_friend_{i}",
                email=f"friend{i}@profile.test",
                first_name=f"Friend",
                last_name=f"Number{i}",
            )
            cls.friend_users.append(friend)
            # Add as friend
            cls.test_user.profile.friends.add(friend)

        # Create another user for permission testing
        cls.other_user = User.objects.create_user(
            username="profile_test_other", email="other@profile.test"
        )

    def setUp(self):
        """Set up authenticated client for each test."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_profile_retrieval_basic(self):
        """
        Test basic profile retrieval performance.
        """
        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("basic_profile_retrieval") as monitor:
                response = self.client.get(
                    f"/api/users/{self.test_user.profile.pk}/profile/"
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["user"], self.test_user.pk)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 150, "Profile retrieval should be fast"
            )
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
            self.assertQueriesLess(monitor.metrics, 10, "Should use optimized queries")
        else:
            # Fallback without monitoring
            response = self.client.get(
                f"/api/users/{self.test_user.profile.pk}/profile/"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_with_many_friends(self):
        """
        Test profile retrieval with many friends.

        This test verifies that the ProfileSerializer properly handles
        the friends relationship without N+1 queries.
        """
        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("profile_with_friends") as monitor:
                response = self.client.get(
                    f"/api/users/{self.test_user.profile.pk}/profile/"
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("friends", response.data)
            self.assertEqual(len(response.data["friends"]), 20)

            # Performance assertions - should NOT have N+1 queries
            self.assertResponseTimeLess(
                monitor.metrics, 200, "Should handle many friends efficiently"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Memory usage should be controlled"
            )
            self.assertQueriesLess(
                monitor.metrics, 15, "Should avoid N+1 queries with prefetch_related"
            )
        else:
            response = self.client.get(
                f"/api/users/{self.test_user.profile.pk}/profile/"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["friends"]), 20)

    def test_profile_update_performance(self):
        """
        Test profile update operation performance.
        """
        update_data = {
            "bio": "Updated bio for performance testing",
            "occupation": "performance_tester",
            "country": "US",
        }

        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("profile_update") as monitor:
                response = self.client.patch(
                    f"/api/users/{self.test_user.profile.pk}/profile/",
                    data=json.dumps(update_data),
                    content_type="application/json",
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["bio"], update_data["bio"])

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 200, "Profile update should be reasonably fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Update should use minimal memory"
            )
            self.assertQueriesLess(
                monitor.metrics, 10, "Update should minimize queries"
            )
        else:
            response = self.client.patch(
                f"/api/users/{self.test_user.profile.pk}/profile/",
                data=json.dumps(update_data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multiple_profile_retrievals(self):
        """
        Test multiple sequential profile retrievals.

        This simulates viewing multiple friend profiles in sequence.
        """
        profiles_to_check = [self.test_user] + self.friend_users[:5]

        if MERCURY_AVAILABLE:
            # Monitor all retrievals together
            with monitor_django_view("multiple_profiles") as monitor:
                for user in profiles_to_check:
                    response = self.client.get(f"/api/users/{user.profile.pk}/profile/")
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Performance assertions for the batch
            self.assertResponseTimeLess(
                monitor.metrics, 600, "6 profiles should complete reasonably fast"
            )
            self.assertMemoryLess(monitor.metrics, 200, "Batch retrieval memory usage")
            # Expect ~10 queries per profile, so 60 total is reasonable
            self.assertQueriesLess(
                monitor.metrics, 60, "Should scale linearly with profile count"
            )
        else:
            for user in profiles_to_check:
                response = self.client.get(f"/api/users/{user.profile.pk}/profile/")
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_profile_retrieval(self):
        """
        Test retrieving another user's profile.

        This tests the permission checks and their performance impact.
        """
        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("other_user_profile") as monitor:
                response = self.client.get(
                    f"/api/users/{self.other_user.profile.pk}/profile/"
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 150, "Permission checks should be fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Permission checks should use minimal memory"
            )
            self.assertQueriesLess(
                monitor.metrics, 10, "Permission checks should be optimized"
            )
        else:
            response = self.client.get(
                f"/api/users/{self.other_user.profile.pk}/profile/"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_retrieval_empty_friends(self):
        """
        Test profile retrieval with no friends for baseline performance.
        """
        # Use other_user who has no friends
        empty_client = APIClient()
        empty_client.force_authenticate(user=self.other_user)

        if MERCURY_AVAILABLE:
            # Monitor the API call
            with monitor_django_view("empty_friends_profile") as monitor:
                response = empty_client.get(
                    f"/api/users/{self.other_user.profile.pk}/profile/"
                )

            # Regular assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["friends"]), 0)

            # Performance assertions - should be very fast with no relationships
            self.assertResponseTimeLess(
                monitor.metrics, 100, "Empty profile should be very fast"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Empty profile should use minimal memory"
            )
            self.assertQueriesLess(
                monitor.metrics, 5, "Empty profile should use minimal queries"
            )
        else:
            response = empty_client.get(
                f"/api/users/{self.other_user.profile.pk}/profile/"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["friends"]), 0)
