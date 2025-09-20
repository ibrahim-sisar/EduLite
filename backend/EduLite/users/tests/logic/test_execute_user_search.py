# users/tests/logic/test_execute_user_search.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework import status

from users.logic.user_search_logic import execute_user_search
from users.models import UserProfilePrivacySettings


class ExecuteUserSearchTest(TestCase):
    """Test the execute_user_search function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create test users with various privacy settings
        cls.public_user = User.objects.create_user(
            username="public_john", first_name="John", last_name="Public"
        )
        cls.public_user.profile.privacy_settings.search_visibility = "everyone"
        cls.public_user.profile.privacy_settings.save()

        cls.private_user = User.objects.create_user(
            username="private_jane", first_name="Jane", last_name="Private"
        )
        cls.private_user.profile.privacy_settings.search_visibility = "friends_only"
        cls.private_user.profile.privacy_settings.save()

        cls.fof_user = User.objects.create_user(
            username="fof_user", first_name="Friends", last_name="OfFriends"
        )
        cls.fof_user.profile.privacy_settings.search_visibility = "friends_of_friends"
        cls.fof_user.profile.privacy_settings.save()

        # Create searcher
        cls.searcher = User.objects.create_user(
            username="searcher", first_name="Search", last_name="User"
        )

        # Make searcher friends with private_user
        cls.searcher.profile.friends.add(cls.private_user)
        cls.private_user.profile.friends.add(cls.searcher)

        # Create admin user
        cls.admin_user = User.objects.create_user(
            username="admin", password="admin123", is_staff=True, is_superuser=True
        )

        # Mock view
        class MockView(APIView):
            pass

        cls.mock_view = MockView()

    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()

    def test_successful_search_with_valid_query(self):
        """Test successful search with valid query."""
        request = self.factory.get("/api/users/search/", {"q": "john"})

        success, queryset, paginator, error = execute_user_search(
            search_query="john",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        self.assertIsNotNone(queryset)
        self.assertIsNotNone(paginator)
        self.assertIsNone(error)

        # Should find public_john
        page = paginator.page
        usernames = [u.username for u in page]
        self.assertIn("public_john", usernames)

    def test_search_with_empty_query(self):
        """Test search with empty query returns error."""
        request = self.factory.get("/api/users/search/", {"q": ""})

        success, queryset, paginator, error = execute_user_search(
            search_query="",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertFalse(success)
        self.assertIsNone(queryset)
        self.assertIsNone(paginator)
        self.assertIsNotNone(error)
        self.assertEqual(error.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error.data["detail"], "Search query is required.")

    def test_search_with_short_query(self):
        """Test search with query below minimum length."""
        request = self.factory.get("/api/users/search/", {"q": "a"})

        success, queryset, paginator, error = execute_user_search(
            search_query="a",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
            min_query_length=2,
        )

        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertEqual(
            error.data["detail"], "Search query must be at least 2 characters long."
        )

    def test_search_with_custom_min_length(self):
        """Test search with custom minimum query length."""
        request = self.factory.get("/api/users/search/", {"q": "jo"})

        # Should fail with min_length=3
        success, _, _, error = execute_user_search(
            search_query="jo",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
            min_query_length=3,
        )

        self.assertFalse(success)
        self.assertIsNotNone(error)

        # Should succeed with min_length=2
        success, _, _, error = execute_user_search(
            search_query="jo",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
            min_query_length=2,
        )

        self.assertTrue(success)
        self.assertIsNone(error)

    def test_search_respects_privacy_filters(self):
        """Test that search respects privacy filters."""
        request = self.factory.get("/api/users/search/", {"q": "user"})

        # Anonymous search
        success, _, paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=None,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        # Anonymous should only see public users
        page = paginator.page
        for user in page:
            if hasattr(user.profile, "privacy_settings"):
                self.assertEqual(
                    user.profile.privacy_settings.search_visibility, "everyone"
                )

    def test_search_with_authenticated_user(self):
        """Test search with authenticated user sees appropriate results."""
        request = self.factory.get("/api/users/search/", {"q": "jane"})

        success, _, paginator, _ = execute_user_search(
            search_query="jane",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        # Should see private_jane (friend)
        page = paginator.page
        usernames = [u.username for u in page]
        self.assertIn("private_jane", usernames)

    def test_admin_bypass_privacy_filters(self):
        """Test that admin can bypass privacy filters."""
        request = self.factory.get("/api/users/search/", {"q": "user"})

        # Admin search with bypass
        success, _, paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=self.admin_user,
            request=request,
            view_instance=self.mock_view,
            bypass_privacy_filters=True,
        )

        self.assertTrue(success)
        # Admin should see all users
        page = paginator.page
        usernames = [u.username for u in page]
        # Should see users regardless of privacy settings
        self.assertGreater(len(usernames), 0)

    def test_search_with_custom_page_size(self):
        """Test search with custom page size."""
        # Create more users for pagination
        for i in range(15):
            User.objects.create_user(username=f"test_user_{i}", first_name="Test")

        request = self.factory.get("/api/users/search/", {"q": "test"})

        success, _, paginator, _ = execute_user_search(
            search_query="test",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
            page_size=5,
        )

        self.assertTrue(success)
        self.assertEqual(paginator.page_size, 5)
        page = paginator.page
        self.assertLessEqual(len(page), 5)

    def test_search_pagination(self):
        """Test search with pagination parameters."""
        # First, create enough users to have page 2
        for i in range(5):
            User.objects.create_user(username=f"user_page_test_{i}")

        request = self.factory.get("/api/users/search/", {"q": "user", "page": "2"})

        success, _, paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
            page_size=3,  # With 5+ users, page 2 should exist
        )

        self.assertTrue(success)
        # Should be on page 2
        self.assertIsNotNone(paginator)

    def test_search_no_results(self):
        """Test search that returns no results."""
        request = self.factory.get("/api/users/search/", {"q": "nonexistent"})

        success, _, paginator, _ = execute_user_search(
            search_query="nonexistent",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        page = paginator.page
        self.assertEqual(len(page), 0)

    def test_search_ordering(self):
        """Test that search results are ordered by username."""
        # Create users with specific usernames
        User.objects.create_user(username="aaa_test", first_name="Test")
        User.objects.create_user(username="zzz_test", first_name="Test")
        User.objects.create_user(username="mmm_test", first_name="Test")

        request = self.factory.get("/api/users/search/", {"q": "test"})

        success, _, paginator, _ = execute_user_search(
            search_query="test",
            requesting_user=self.searcher,
            request=request,
            view_instance=self.mock_view,
            page_size=20,
        )

        self.assertTrue(success)
        page = paginator.page
        usernames = [u.username for u in page if "test" in u.username]

        # Check ordering
        sorted_usernames = sorted(usernames)
        self.assertEqual(usernames, sorted_usernames)
