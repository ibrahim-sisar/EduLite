# users/tests/logic/test_user_search_integration.py

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from users.logic.user_search_logic import (
    execute_user_search,
    filter_user_display_data,
    have_mutual_friends,
)
from users.tests.fixtures.test_data_generators import (
    create_students_bulk,
    create_teachers_bulk,
    setup_friend_relationships,
    create_users_with_privacy_variations,
)


class UserSearchIntegrationTest(TestCase):
    """Integration tests for user search logic."""

    @classmethod
    def setUpTestData(cls):
        """Create comprehensive test data."""
        # Create realistic personas
        cls.students = create_students_bulk()
        cls.teachers = create_teachers_bulk()

        # Set up friend relationships
        setup_friend_relationships(cls.students, cls.teachers)

        # Create users with various privacy settings
        cls.privacy_users = create_users_with_privacy_variations()

        # Create additional test users
        cls.admin = User.objects.create_user(
            username="admin", password="admin123", is_staff=True, is_superuser=True
        )

        # Mock view
        class MockView(APIView):
            pass

        cls.mock_view = MockView()

    def setUp(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()

    def test_realistic_search_scenario_arabic_name(self):
        """Test searching for Arabic names."""
        request = self.factory.get("/api/users/search/", {"q": "ahmad"})

        # Ahmad from Gaza searching
        searcher = self.students["ahmad"]

        success, _, paginator, _ = execute_user_search(
            search_query="ahmad",
            requesting_user=searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        page = paginator.page

        # Should find users with ahmad in their name/username
        usernames = [u.username for u in page]
        # Should at least find the searcher themselves and any other ahmad users
        self.assertGreater(len(usernames), 0)

    def test_privacy_aware_search_friends_network(self):
        """Test search respecting friend networks."""
        request = self.factory.get("/api/users/search/", {"q": "student"})

        # Marie searching (has specific friends)
        searcher = self.students["marie"]

        success, _, paginator, _ = execute_user_search(
            search_query="student",
            requesting_user=searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        page = paginator.page

        # Should see friends and public users
        for user in page:
            if user != searcher:  # Skip self
                is_friend = searcher.profile.friends.filter(id=user.id).exists()
                is_public = (
                    user.profile.privacy_settings.search_visibility == "everyone"
                )
                is_fof = (
                    user.profile.privacy_settings.search_visibility
                    == "friends_of_friends"
                    and have_mutual_friends(searcher, user)
                )

                self.assertTrue(
                    is_friend or is_public or is_fof,
                    f"User {user.username} should not be visible to {searcher.username}",
                )

    def test_teacher_searching_for_students(self):
        """Test teacher searching for students."""
        request = self.factory.get("/api/users/search/", {"q": "student"})

        # Teacher Sarah searching
        searcher = self.teachers["sarah"]

        success, _, paginator, _ = execute_user_search(
            search_query="student",
            requesting_user=searcher,
            request=request,
            view_instance=self.mock_view,
            page_size=20,
        )

        self.assertTrue(success)
        page = paginator.page

        # Teachers often have public profiles and can see more students
        self.assertGreater(len(page), 0)

    def test_anonymous_search_limited_results(self):
        """Test anonymous users get limited results."""
        request = self.factory.get("/api/users/search/", {"q": "user"})

        # Anonymous search
        success, _, paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=None,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        page = paginator.page

        # All results should be public
        for user in page:
            self.assertEqual(
                user.profile.privacy_settings.search_visibility, "everyone"
            )

    def test_admin_bypass_sees_all(self):
        """Test admin bypass sees all users."""
        request = self.factory.get("/api/users/search/", {"q": "user"})

        # Get counts for comparison
        normal_success, _, normal_paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=self.admin,
            request=request,
            view_instance=self.mock_view,
            bypass_privacy_filters=False,
        )

        bypass_success, _, bypass_paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=self.admin,
            request=request,
            view_instance=self.mock_view,
            bypass_privacy_filters=True,
        )

        self.assertTrue(normal_success)
        self.assertTrue(bypass_success)

        # Admin with bypass should see more or equal users
        normal_count = len(normal_paginator.page)
        bypass_count = len(bypass_paginator.page)
        self.assertGreaterEqual(bypass_count, normal_count)

    def test_search_performance_with_large_dataset(self):
        """Test search performance with many users."""
        # Create 100 additional users
        for i in range(100):
            user = User.objects.create_user(
                username=f"perf_user_{i}",
                first_name="Performance",
                last_name=f"Test{i}",
            )
            # Vary privacy settings
            visibility_options = [
                "everyone",
                "friends_only",
                "friends_of_friends",
                "nobody",
            ]
            user.profile.privacy_settings.search_visibility = visibility_options[i % 4]
            user.profile.privacy_settings.save()

        request = self.factory.get("/api/users/search/", {"q": "perf"})

        # Should complete quickly even with many users
        with self.assertNumQueries(4):  # Reasonable query count
            success, _, paginator, _ = execute_user_search(
                search_query="perf",
                requesting_user=self.students["ahmad"],
                request=request,
                view_instance=self.mock_view,
            )

        self.assertTrue(success)

    def test_filter_user_display_data_passthrough(self):
        """Test filter_user_display_data function (currently passthrough)."""
        users = User.objects.all()[:5]

        # Should return same queryset
        filtered = filter_user_display_data(users, self.students["ahmad"])

        self.assertEqual(list(users), list(filtered))

    def test_complex_privacy_scenarios(self):
        """Test complex privacy scenarios."""
        # Get privacy test users
        private_user = next(
            u for u in self.privacy_users if u.username == "private_user"
        )
        public_user = next(u for u in self.privacy_users if u.username == "public_user")
        fof_user = next(
            u for u in self.privacy_users if u.username == "friends_of_friends_user"
        )

        # Create searcher with specific relationships
        searcher = User.objects.create_user(username="searcher")
        mutual_friend = User.objects.create_user(username="mutual")

        # Set up relationships
        searcher.profile.friends.add(mutual_friend)
        fof_user.profile.friends.add(mutual_friend)

        request = self.factory.get("/api/users/search/", {"q": "user"})

        success, _, paginator, _ = execute_user_search(
            search_query="user",
            requesting_user=searcher,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        page = paginator.page
        usernames = [u.username for u in page]

        # Should see public_user
        self.assertIn("public_user", usernames)
        # May or may not see fof_user depending on mutual friend setup
        # Should not see private_user (not friends)
        self.assertNotIn("private_user", usernames)

    def test_search_with_special_characters(self):
        """Test search with special characters."""
        # Create user with special characters
        special_user = User.objects.create_user(
            username="user@special#123", first_name="Special-Name", last_name="O'Connor"
        )

        request = self.factory.get("/api/users/search/", {"q": "O'Connor"})

        success, _, paginator, _ = execute_user_search(
            search_query="O'Connor",
            requesting_user=self.admin,
            request=request,
            view_instance=self.mock_view,
        )

        self.assertTrue(success)
        page = paginator.page

        # Should find the user with apostrophe in name
        last_names = [u.last_name for u in page]
        self.assertIn("O'Connor", last_names)
