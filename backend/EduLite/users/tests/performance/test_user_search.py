# users/tests/performance/test_user_search_performance.py - Performance tests for UserSearchView
"""
Performance testing for UserSearchView using Mercury framework.

Tests search performance across different scenarios:
- Different user contexts (anonymous, authenticated, admin)
- Various dataset sizes using fixtures and bulk creation
- Complex privacy filtering and friend relationships
- Query optimization validation
"""

from django.contrib.auth.models import User
from django.test import TransactionTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

# Import Mercury performance testing framework
from django_mercury import DjangoPerformanceAPITestCase, monitor_django_view

MERCURY_AVAILABLE = True

from ...models import UserProfile, UserProfilePrivacySettings
from ..fixtures.bulk_test_users import create_bulk_test_users


class UserSearchPerformanceTest(DjangoPerformanceAPITestCase):
    """
    Performance test suite for UserSearchView with Mercury framework.

    Tests search performance across different contexts and dataset sizes,
    focusing on the complex privacy filtering and friend relationship queries.
    """

    # Don't use fixtures to avoid profile creation conflicts

    # Removed setUpClass - not needed for DjangoPerformanceAPITestCase
    # DjangoPerformanceAPITestCase uses manual monitoring with specific assertions

    def setUp(self):
        """Set up test data for each test."""
        super().setUp()

        # Clean up any existing test data to avoid conflicts
        # Use CASCADE to ensure related objects are deleted
        test_prefixes = ["perf_user", "search_user", "admin_user", "john_doe_"]
        for prefix in test_prefixes:
            User.objects.filter(username__startswith=prefix).delete()

        # Set up test clients
        self.anonymous_client = APIClient()

        # Create a test user for authentication
        self.authenticated_user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        self.authenticated_client = APIClient()
        self.authenticated_client.force_authenticate(user=self.authenticated_user)

        # Create admin user for tests
        self.admin_user = User.objects.create_user(
            username="test_admin",
            email="admin@test.com",
            is_superuser=True,
            is_staff=True,
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

    def create_test_users_with_relationships(self, user_count: int):
        """
        Create test users with realistic privacy settings and friend relationships.

        Args:
            user_count: Number of users to create

        Returns:
            List of created users
        """
        # Create bulk users efficiently with unique prefix
        import time

        unique_prefix = f"perf_user_{int(time.time() * 1000)}"
        users = create_bulk_test_users(unique_prefix, user_count)

        # Set up varied privacy settings
        # Since bulk_create bypasses signals, we need to manually create privacy settings
        # But we must check if they already exist (in case of signal creation)
        for i, user in enumerate(users):
            if i % 3 == 0:
                visibility = "everyone"
            elif i % 3 == 1:
                visibility = "friends_only"
            else:
                visibility = "friends_of_friends"

            # Use update_or_create to handle both cases
            UserProfilePrivacySettings.objects.update_or_create(
                user_profile=user.profile,
                defaults={
                    "search_visibility": visibility,
                    "profile_visibility": visibility,
                    "show_full_name": True,
                    "show_email": False,
                    "allow_friend_requests": True,
                },
            )

        # Create friend relationships (every 5th user is friends with authenticated_user)
        friends_to_add = []
        for i, user in enumerate(users):
            if i % 5 == 0:
                friends_to_add.append(user)

        if friends_to_add:
            self.authenticated_user.profile.friends.add(*friends_to_add)

        # Create mutual friendships for friends-of-friends testing
        if len(users) >= 10:
            # Make first 10 users friends with each other
            for i in range(5):
                if i < len(users) - 1:
                    users[i].profile.friends.add(users[i + 5])

        return users

    # --- Basic Search Performance Tests ---

    def test_simple_search_performance(self):
        """Test basic search performance with small dataset."""
        # Create some test users
        self.create_test_users_with_relationships(25)

        if MERCURY_AVAILABLE:
            # Monitor the search operation
            with monitor_django_view("simple_search") as monitor:
                response = self.authenticated_client.get(
                    "/api/users/search/?q=perf_user"
                )

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            self.assertGreater(len(response.data["results"]), 0)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 100, "Simple search should be fast"
            )
            self.assertQueriesLess(monitor.metrics, 5, "Should use optimized queries")
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
        else:
            # Fallback with assertNumQueries when Mercury not available
            with self.assertNumQueries(
                4
            ):  # 1 friend lookup + 1 count + 1 search + 1 groups prefetch
                response = self.authenticated_client.get(
                    "/api/users/search/?q=perf_user"
                )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            self.assertGreater(len(response.data["results"]), 0)

    def test_empty_search_performance(self):
        """Test performance when search returns no results."""
        if MERCURY_AVAILABLE:
            # Monitor empty search
            with monitor_django_view("empty_search") as monitor:
                response = self.authenticated_client.get(
                    "/api/users/search/?q=nonexistentuser123"
                )

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 0)

            # Performance assertions - should be very fast with no results
            self.assertResponseTimeLess(
                monitor.metrics, 50, "Empty search should be very fast"
            )
            self.assertQueriesLess(
                monitor.metrics, 3, "Empty search should use minimal queries"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Empty search should use minimal memory"
            )
        else:
            # Fallback with assertNumQueries
            with self.assertNumQueries(
                2
            ):  # 1 friend lookup + 1 count (no results, no prefetch)
                response = self.authenticated_client.get(
                    "/api/users/search/?q=nonexistentuser123"
                )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["results"]), 0)

    # --- Context-Based Performance Tests ---

    def test_anonymous_user_search_performance(self):
        """Test search performance for anonymous users."""
        # Create users with varying privacy settings
        self.create_test_users_with_relationships(50)

        if MERCURY_AVAILABLE:
            # Monitor anonymous search
            with monitor_django_view("anonymous_search") as monitor:
                response = self.anonymous_client.get("/api/users/search/?q=perf_user")

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Check that results respect privacy settings
            for user_data in response.data["results"]:
                user = User.objects.get(username=user_data["username"])
                self.assertEqual(
                    user.profile.privacy_settings.search_visibility, "everyone"
                )

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 150, "Anonymous search should be reasonably fast"
            )
            self.assertQueriesLess(
                monitor.metrics,
                10,
                "Should use reasonable queries for privacy filtering",
            )
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
        else:
            response = self.anonymous_client.get("/api/users/search/?q=perf_user")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            for user_data in response.data["results"]:
                user = User.objects.get(username=user_data["username"])
                self.assertEqual(
                    user.profile.privacy_settings.search_visibility, "everyone"
                )

    def test_authenticated_user_search_performance(self):
        """Test search performance for authenticated users."""
        # Create users with varying privacy settings
        self.create_test_users_with_relationships(50)

        if MERCURY_AVAILABLE:
            # Monitor authenticated search
            with monitor_django_view("authenticated_search") as monitor:
                response = self.authenticated_client.get(
                    "/api/users/search/?q=perf_user"
                )

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            self.assertGreater(len(response.data["results"]), 0)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 150, "Authenticated search should be fast"
            )
            self.assertQueriesLess(
                monitor.metrics, 5, "Should maintain optimized query count"
            )
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
        else:
            # Fallback with assertNumQueries
            with self.assertNumQueries(4):
                response = self.authenticated_client.get(
                    "/api/users/search/?q=perf_user"
                )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            self.assertGreater(len(response.data["results"]), 0)

    def test_admin_user_search_performance(self):
        """Test search performance for admin users."""
        # Create users with varying privacy settings
        self.create_test_users_with_relationships(50)

        if MERCURY_AVAILABLE:
            # Monitor admin search
            with monitor_django_view("admin_search") as monitor:
                response = self.admin_client.get("/api/users/search/?q=perf_user")

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Admin should see more results than regular users
            admin_results = len(response.data["results"])

            # Compare with regular user results
            regular_response = self.authenticated_client.get(
                "/api/users/search/?q=perf_user"
            )
            regular_results = len(regular_response.data["results"])

            self.assertGreaterEqual(admin_results, regular_results)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 50, "Admin search should be fast"
            )
            self.assertQueriesLess(
                monitor.metrics, 5, "Admin search should be optimized"
            )
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
        else:
            response = self.admin_client.get("/api/users/search/?q=perf_user")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            admin_results = len(response.data["results"])
            regular_response = self.authenticated_client.get(
                "/api/users/search/?q=perf_user"
            )
            regular_results = len(regular_response.data["results"])
            self.assertGreaterEqual(admin_results, regular_results)

    # --- Scalability Tests ---

    def test_medium_dataset_performance(self):
        """Test search performance with medium dataset."""
        # Create additional users for testing
        self.create_test_users_with_relationships(100)

        if MERCURY_AVAILABLE:
            # Monitor search with medium dataset
            with monitor_django_view("medium_dataset_search") as monitor:
                response = self.authenticated_client.get("/api/users/search/?q=perf")

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            # Check pagination is working
            self.assertIn("count", response.data)
            self.assertIn("next", response.data)

            # Performance assertions - slightly more lenient for larger dataset
            self.assertResponseTimeLess(
                monitor.metrics, 200, "Medium dataset search should still be fast"
            )
            self.assertQueriesLess(
                monitor.metrics, 10, "Should maintain query efficiency with more data"
            )
            self.assertMemoryLess(
                monitor.metrics, 200, "May use more memory with larger dataset"
            )
        else:
            response = self.authenticated_client.get("/api/users/search/?q=perf")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("results", response.data)
            self.assertIn("count", response.data)
            self.assertIn("next", response.data)

    def test_search_with_pagination(self):
        """Test search pagination performance."""
        # Create some additional users
        self.create_test_users_with_relationships(50)

        # Test different page sizes
        for page_size in [5, 10, 20]:
            if MERCURY_AVAILABLE:
                # Monitor paginated search
                with monitor_django_view(f"search_pagination_{page_size}") as monitor:
                    response = self.authenticated_client.get(
                        f"/api/users/search/?q=perf_user&page_size={page_size}"
                    )

                # Functional assertions
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertLessEqual(len(response.data["results"]), page_size)

                # Performance assertions
                self.assertResponseTimeLess(
                    monitor.metrics, 150, f"Page size {page_size} should be fast"
                )
                self.assertQueriesLess(
                    monitor.metrics, 5, "Pagination should be optimized"
                )
                self.assertMemoryLess(
                    monitor.metrics, 150, "Should use reasonable memory"
                )
            else:
                # Fallback with query counting
                from django.test.utils import CaptureQueriesContext
                from django.db import connection

                with CaptureQueriesContext(connection) as queries:
                    response = self.authenticated_client.get(
                        f"/api/users/search/?q=perf_user&page_size={page_size}"
                    )

                query_count = len(queries)
                self.assertIn(
                    query_count,
                    [3, 4],
                    f"Expected 3-4 queries for search, got {query_count}",
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertLessEqual(len(response.data["results"]), page_size)

    # --- Friend Relationship Tests ---

    def test_friends_relationship_search(self):
        """Test search with friend relationships."""
        # Create users with friend relationships
        users = self.create_test_users_with_relationships(20)

        # Make the authenticated user friends with some users
        # Note: friends field expects User objects, not UserProfile objects
        self.authenticated_user.profile.friends.add(users[0])
        self.authenticated_user.profile.friends.add(users[1])

        if MERCURY_AVAILABLE:
            # Monitor search with friend relationships
            with monitor_django_view("friends_search") as monitor:
                response = self.authenticated_client.get(
                    "/api/users/search/?q=perf_user"
                )

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data["results"]), 0)

            # Performance assertions
            self.assertResponseTimeLess(
                monitor.metrics, 150, "Friends search should be fast"
            )
            self.assertQueriesLess(
                monitor.metrics, 10, "Friend relationships may require more queries"
            )
            self.assertMemoryLess(monitor.metrics, 150, "Should use reasonable memory")
        else:
            response = self.authenticated_client.get("/api/users/search/?q=perf_user")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data["results"]), 0)

    # --- Edge Case Performance Tests ---

    def test_common_search_term_performance(self):
        """Test performance with very common search terms (many matches)."""
        # Create users where many match the search term
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f"john_doe_{i}",
                email=f"john{i}@test.com",
                first_name="John",
                last_name="Doe",
            )
            users.append(user)

        # Set up privacy settings - use get_or_create to avoid duplicates
        for user in users:
            UserProfilePrivacySettings.objects.get_or_create(
                user_profile=user.profile, defaults={"search_visibility": "everyone"}
            )

        if MERCURY_AVAILABLE:
            # Monitor search with common term
            with monitor_django_view("common_term_search") as monitor:
                response = self.authenticated_client.get("/api/users/search/?q=john")

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data["results"]), 0)

            # Performance assertions - slightly more lenient for many matches
            self.assertResponseTimeLess(
                monitor.metrics,
                300,
                "Common term search should handle many results well",
            )
            self.assertQueriesLess(
                monitor.metrics, 5, "Should still be optimized despite many matches"
            )
            self.assertMemoryLess(
                monitor.metrics, 200, "May use more memory with many results"
            )
        else:
            # Fallback with assertNumQueries
            with self.assertNumQueries(
                4
            ):  # Still optimized to 4 queries for search itself
                response = self.authenticated_client.get("/api/users/search/?q=john")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreater(len(response.data["results"]), 0)

    def test_pagination_performance(self):
        """Test search performance across different pagination scenarios."""
        self.create_test_users_with_relationships(200)

        page_sizes = [5, 10, 20]

        for page_size in page_sizes:
            with self.subTest(page_size=page_size):
                if MERCURY_AVAILABLE:
                    # Monitor paginated search
                    with monitor_django_view(
                        f"paginated_search_{page_size}"
                    ) as monitor:
                        response = self.authenticated_client.get(
                            f"/api/users/search/?q=perf_user&page_size={page_size}"
                        )

                    # Functional assertions
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertLessEqual(len(response.data["results"]), page_size)

                    # Performance assertions - should be consistent regardless of page size
                    self.assertResponseTimeLess(
                        monitor.metrics,
                        200,
                        f"Pagination with size {page_size} should be fast",
                    )
                    self.assertQueriesLess(
                        monitor.metrics,
                        5,
                        "Pagination should maintain query efficiency",
                    )
                    self.assertMemoryLess(
                        monitor.metrics, 150, "Pagination should limit memory usage"
                    )
                else:
                    # Fallback with query counting
                    from django.test.utils import CaptureQueriesContext
                    from django.db import connection

                    with CaptureQueriesContext(connection) as queries:
                        response = self.authenticated_client.get(
                            f"/api/users/search/?q=perf_user&page_size={page_size}"
                        )

                    query_count = len(queries)
                    self.assertIn(
                        query_count,
                        [3, 4],
                        f"Expected 3-4 queries for search, got {query_count}",
                    )

                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertLessEqual(len(response.data["results"]), page_size)

    def test_search_with_special_characters(self):
        """Test search with special characters."""
        # Test that special characters are handled properly
        special_queries = ["user@test", "user+test", "user%20test"]

        for query in special_queries:
            if MERCURY_AVAILABLE:
                # Monitor search with special characters
                with monitor_django_view(
                    f"special_char_search_{query[:10]}"
                ) as monitor:
                    response = self.authenticated_client.get(
                        f"/api/users/search/?q={query}"
                    )

                # Functional assertions
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Performance assertions - should be fast even with special chars
                self.assertResponseTimeLess(
                    monitor.metrics, 100, "Special character handling should be fast"
                )
                self.assertQueriesLess(monitor.metrics, 5, "Should maintain efficiency")
                self.assertMemoryLess(
                    monitor.metrics, 150, "Should use reasonable memory"
                )
            else:
                response = self.authenticated_client.get(
                    f"/api/users/search/?q={query}"
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_minimum_length(self):
        """Test search minimum query length."""
        if MERCURY_AVAILABLE:
            # Monitor minimum length validation
            with monitor_django_view("min_length_search") as monitor:
                response = self.authenticated_client.get("/api/users/search/?q=a")

            # Functional assertions
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("at least 2 characters", response.data.get("detail", ""))

            # Performance assertions - validation should be instant
            self.assertResponseTimeLess(
                monitor.metrics, 50, "Validation should be very fast"
            )
            self.assertQueriesLess(
                monitor.metrics, 2, "Validation should require minimal queries"
            )
            self.assertMemoryLess(
                monitor.metrics, 150, "Validation should use minimal memory"
            )
        else:
            response = self.authenticated_client.get("/api/users/search/?q=a")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("at least 2 characters", response.data.get("detail", ""))


if __name__ == "__main__":
    # Run the performance test suite
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(UserSearchPerformanceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
