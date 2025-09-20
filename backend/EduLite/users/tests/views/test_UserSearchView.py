# users/tests/views/test_UserSearchView.py - Tests for UserSearchView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .. import UsersAppTestCase


class UserSearchViewTest(UsersAppTestCase):
    """Test cases for the UserSearchView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = reverse("user-search")

    # --- Authentication Tests ---

    def test_anonymous_users_can_search(self):
        """Test that anonymous users can search but with limited visibility."""
        # Create a user with 'everyone' visibility
        public_user = User.objects.create_user(
            username="public_user",
            email="public@test.com",
            first_name="Public",
            last_name="User",
        )
        public_user.profile.privacy_settings.search_visibility = "everyone"
        public_user.profile.privacy_settings.save()

        # Create a user with 'friends_only' visibility
        private_user = User.objects.create_user(
            username="private_user",
            email="private@test.com",
            first_name="Private",
            last_name="User",
        )
        private_user.profile.privacy_settings.search_visibility = "friends_only"
        private_user.profile.privacy_settings.save()

        # Anonymous search should only find the public user
        response = self.client.get(self.url, {"q": "user"})
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_paginated_response(response)

        # Check that only public user is visible
        usernames = [user["username"] for user in response.data["results"]]
        self.assertIn("public_user", usernames)
        self.assertNotIn("private_user", usernames)

    def test_search_authenticated_success(self):
        """Test that authenticated users can search."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"q": "marie"})
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_paginated_response(response)

    # --- Query Validation Tests ---

    def test_search_empty_query(self):
        """Test search with empty query parameter."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"q": ""})
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertIn("required", response.data["detail"].lower())

    def test_search_no_query_parameter(self):
        """Test search without query parameter."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)

    def test_search_whitespace_only_query(self):
        """Test search with whitespace-only query."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"q": "   "})
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)

    def test_search_query_too_short(self):
        """Test search with query shorter than minimum length."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"q": "a"})
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("at least 2 characters", response.data["detail"])

    def test_search_query_minimum_length(self):
        """Test search with minimum valid query length."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"q": "ah"})
        self.assert_response_success(response, status.HTTP_200_OK)

    # --- Basic Search Functionality ---

    def test_search_by_username(self):
        """Test searching users by username."""
        self.authenticate_as(self.ahmad)

        # Search for 'marie' should find marie_student
        response = self.client.get(self.url, {"q": "marie"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("marie_student", usernames)

    def test_search_by_first_name(self):
        """Test searching users by first name."""
        # Use Elena who is friends with Joy (Joy has friends_only visibility)
        self.authenticate_as(self.elena)

        # Search for 'Joy' should find Joy Okoro
        response = self.client.get(self.url, {"q": "Joy"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("joy_student", usernames)

    def test_search_by_last_name(self):
        """Test searching users by last name."""
        # Use Elena who is friends with Joy (Joy has friends_only visibility)
        self.authenticate_as(self.elena)

        # Search for 'Okoro' should find Joy Okoro
        response = self.client.get(self.url, {"q": "Okoro"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("joy_student", usernames)

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        self.authenticate_as(self.ahmad)

        # Search with different cases
        test_cases = ["MARIE", "Marie", "marie", "mArIe"]

        for query in test_cases:
            with self.subTest(query=query):
                response = self.client.get(self.url, {"q": query})
                self.assert_response_success(response, status.HTTP_200_OK)

                usernames = [u["username"] for u in response.data["results"]]
                self.assertIn("marie_student", usernames)

    def test_search_partial_match(self):
        """Test that partial matches work."""
        self.authenticate_as(self.ahmad)

        # 'stud' should match all *_student usernames
        response = self.client.get(self.url, {"q": "stud"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        student_usernames = [u for u in usernames if "student" in u]
        self.assertGreater(len(student_usernames), 0)

    # --- Privacy Filtering Tests ---

    def test_search_respects_nobody_visibility(self):
        """Test that users with search_visibility='nobody' don't appear."""
        self.authenticate_as(self.ahmad)

        # Sophie has search_visibility='nobody'
        response = self.client.get(self.url, {"q": "sophie"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertNotIn("sophie_student", usernames)

    def test_search_everyone_visibility(self):
        """Test that users with search_visibility='everyone' appear to all."""
        self.authenticate_as(self.ahmad)

        # Marie has search_visibility='everyone'
        response = self.client.get(self.url, {"q": "marie"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("marie_student", usernames)

    def test_search_friends_only_visibility(self):
        """Test that users with search_visibility='friends_only' appear only to friends."""
        # Joy has search_visibility='friends_only'

        # Test 1: Non-friend searching (Ahmad is not Joy's friend)
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"q": "joy"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertNotIn("joy_student", usernames)

        # Test 2: Friend searching (Elena is Joy's friend)
        self.authenticate_as(self.elena)
        response = self.client.get(self.url, {"q": "joy"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("joy_student", usernames)

    def test_search_friends_of_friends_visibility(self):
        """Test that users with search_visibility='friends_of_friends' work correctly."""
        # Ahmad has search_visibility='friends_of_friends'
        # Ahmad is friends with Marie
        # Marie is friends with Ahmad

        # Test 1: Direct friend can see (Marie searching for Ahmad)
        self.authenticate_as(self.marie)
        response = self.client.get(self.url, {"q": "ahmad"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("ahmad_gaza", usernames)

        # Test 2: Non-friend/non-FoF cannot see
        # Create a new user with no connections
        isolated_user = self.create_test_user(username="isolated")
        self.authenticate_as(isolated_user)
        response = self.client.get(self.url, {"q": "ahmad"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertNotIn("ahmad_gaza", usernames)

    def test_search_admin_bypasses_privacy(self):
        """Test that admin users can see all users regardless of privacy."""
        admin_user = self.create_test_user(
            username="admin", is_superuser=True, is_staff=True
        )
        self.authenticate_as(admin_user)

        # Admin should see Sophie even though she has visibility='nobody'
        response = self.client.get(self.url, {"q": "sophie"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("sophie_student", usernames)

    # --- Pagination Tests ---

    def test_search_pagination_default_page_size(self):
        """Test that search results are paginated with default page size."""
        self.authenticate_as(self.ahmad)

        # Search for 'student' should return multiple results
        response = self.client.get(self.url, {"q": "student"})
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assert_paginated_response(response)

        # Default page size is 10
        self.assertLessEqual(len(response.data["results"]), 10)

    def test_search_pagination_custom_page_size(self):
        """Test custom page size in search results."""
        self.authenticate_as(self.ahmad)

        # Note: Current implementation doesn't support custom page_size from query params
        # It's hardcoded to 10 in the view
        response = self.client.get(self.url, {"q": "student", "page_size": 5})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should use default page size of 10 (ignores page_size param)
        self.assertLessEqual(len(response.data["results"]), 10)

    def test_search_pagination_navigation(self):
        """Test navigating through paginated search results."""
        self.authenticate_as(self.sarah_teacher)  # Teacher can see more users

        # Create additional test users to ensure multiple pages
        for i in range(15):
            self.create_test_user(username=f"searchtest_{i}", first_name="Searchtest")

        # Search for 'searchtest' (page size is fixed at 10)
        response = self.client.get(self.url, {"q": "searchtest"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should have next page (15 users, 10 per page)
        self.assertIsNotNone(response.data.get("next"))
        self.assertEqual(len(response.data["results"]), 10)

        # Get second page
        response = self.client.get(self.url, {"q": "searchtest", "page": 2})
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("previous"))
        self.assertEqual(len(response.data["results"]), 5)  # Remaining 5 users

    # --- Edge Cases ---

    def test_search_no_results(self):
        """Test search that returns no results."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url, {"q": "nonexistentuser123456"})
        self.assert_response_success(response, status.HTTP_200_OK)

        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_special_characters(self):
        """Test search with special characters."""
        self.authenticate_as(self.ahmad)

        # Create user with special characters
        special_user = self.create_test_user(
            username="test_special", first_name="Jean-Pierre", last_name="O'Connor"
        )

        # Search for name with hyphen
        response = self.client.get(self.url, {"q": "Jean-Pierre"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("test_special", usernames)

    def test_search_unicode_characters(self):
        """Test search with Unicode characters."""
        self.authenticate_as(self.ahmad)

        # Create user with Unicode name
        unicode_user = self.create_test_user(
            username="unicode_test",
            first_name="مُحَمَّد",  # Arabic
            last_name="李",  # Chinese
        )

        # Search with Unicode
        response = self.client.get(self.url, {"q": "مُحَمَّد"})
        self.assert_response_success(response, status.HTTP_200_OK)

        usernames = [u["username"] for u in response.data["results"]]
        self.assertIn("unicode_test", usernames)

    def test_search_sql_injection_attempt(self):
        """Test that SQL injection attempts are handled safely."""
        self.authenticate_as(self.ahmad)

        # Try SQL injection in search query
        response = self.client.get(self.url, {"q": "'; DROP TABLE users; --"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should return results (or no results) but not cause SQL error
        self.assertIn("results", response.data)

        # Verify users table still exists
        self.assertTrue(User.objects.exists())

    def test_search_very_long_query(self):
        """Test search with very long query string."""
        self.authenticate_as(self.ahmad)

        long_query = "a" * 1000
        response = self.client.get(self.url, {"q": long_query})

        # Should handle gracefully (either success or reasonable error)
        self.assertIn(response.status_code, [200, 400])

    # --- Performance Test ---

    def test_search_performance_with_many_users(self):
        """Test that search performance is acceptable with many users."""
        # Create many users
        users = []
        for i in range(100):
            users.append(
                User(
                    username=f"perf_user_{i}",
                    email=f"perf{i}@university.edu",
                    first_name=f"Perf{i}",
                    last_name="User",
                )
            )
        User.objects.bulk_create(users)

        self.authenticate_as(self.ahmad)

        import time

        start_time = time.time()

        # Search for common term
        response = self.client.get(self.url, {"q": "perf"})

        end_time = time.time()
        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertLess(duration, 2.0, "Search took too long")

        # Verify we got paginated results
        self.assertLessEqual(len(response.data["results"]), 10)
