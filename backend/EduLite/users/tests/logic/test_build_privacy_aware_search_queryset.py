# users/tests/logic/test_build_privacy_aware_search_queryset.py

from django.test import TestCase
from django.contrib.auth.models import User

from users.logic.user_search_logic import (
    build_privacy_aware_search_queryset,
    build_base_search_queryset,
)
from users.tests.fixtures.test_data_generators import create_students_bulk


class BuildPrivacyAwareSearchQuerysetTest(TestCase):
    """Test the build_privacy_aware_search_queryset function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data once for all tests."""
        # Create a variety of users with different names
        cls.user1 = User.objects.create_user(
            username="john_doe",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )

        cls.user2 = User.objects.create_user(
            username="jane_smith",
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )

        cls.user3 = User.objects.create_user(
            username="test_user",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )

        # Create users with unicode names
        cls.user4 = User.objects.create_user(
            username="ahmad_arabic",
            first_name="أحمد",
            last_name="محمد",
            email="ahmad@example.com",
        )

        # Create realistic student personas
        cls.students = create_students_bulk()

    def test_search_by_username_exact(self):
        """Test searching by exact username."""
        queryset = build_privacy_aware_search_queryset("john_doe", None)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user1)

    def test_search_by_username_partial(self):
        """Test searching by partial username."""
        queryset = build_privacy_aware_search_queryset("john", None)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user1)

    def test_search_by_first_name(self):
        """Test searching by first name."""
        queryset = build_privacy_aware_search_queryset("Jane", None)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user2)

    def test_search_by_last_name(self):
        """Test searching by last name."""
        queryset = build_privacy_aware_search_queryset("Smith", None)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user2)

    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        # Search with different cases
        queryset1 = build_privacy_aware_search_queryset("JOHN", None)
        queryset2 = build_privacy_aware_search_queryset("john", None)
        queryset3 = build_privacy_aware_search_queryset("JoHn", None)

        self.assertEqual(queryset1.count(), 1)
        self.assertEqual(queryset2.count(), 1)
        self.assertEqual(queryset3.count(), 1)
        self.assertEqual(queryset1.first(), self.user1)

    def test_search_multiple_results(self):
        """Test search that returns multiple results."""
        # Search for 'test' should return test_user
        queryset = build_privacy_aware_search_queryset("test", None)

        self.assertGreaterEqual(queryset.count(), 1)
        self.assertIn(self.user3, queryset)

    def test_search_with_spaces_trimmed(self):
        """Test that search query is trimmed."""
        queryset = build_privacy_aware_search_queryset("  john  ", None)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user1)

    def test_search_unicode_characters(self):
        """Test searching with unicode characters."""
        queryset = build_privacy_aware_search_queryset("أحمد", None)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.user4)

    def test_search_no_results(self):
        """Test search that returns no results."""
        queryset = build_privacy_aware_search_queryset("nonexistent", None)

        self.assertEqual(queryset.count(), 0)

    def test_queryset_optimization(self):
        """Test that queryset has proper select_related and prefetch_related."""
        queryset = build_privacy_aware_search_queryset("john", None)

        # Check that select_related is applied (Django stores it as nested dict)
        select_related = queryset.query.select_related
        self.assertIn("profile", select_related)
        if "profile" in select_related:
            self.assertIn("privacy_settings", select_related["profile"])

        # Check that prefetch_related is applied for groups
        prefetch_lookups = [
            p.prefetch_to if hasattr(p, "prefetch_to") else p
            for p in queryset._prefetch_related_lookups
        ]
        self.assertIn("groups", prefetch_lookups)

    def test_distinct_results(self):
        """Test that results are distinct."""
        # Create a user that might match multiple conditions
        user = User.objects.create_user(
            username="john_johnson", first_name="John", last_name="Johnson"
        )

        # Search for 'john' should return distinct results
        queryset = build_privacy_aware_search_queryset("john", None)

        # Count occurrences of each user
        results = list(queryset)
        user_count = results.count(user)

        self.assertEqual(user_count, 1, "User should appear only once in results")

    def test_ordering_by_username(self):
        """Test that results are ordered by username."""
        # Create users with specific usernames to test ordering
        User.objects.create_user(username="aaa_test", first_name="Test")
        User.objects.create_user(username="zzz_test", first_name="Test")
        User.objects.create_user(username="mmm_test", first_name="Test")

        queryset = build_privacy_aware_search_queryset("test", None)
        usernames = list(queryset.values_list("username", flat=True))

        # Check that usernames are sorted
        sorted_usernames = sorted(usernames)
        self.assertEqual(usernames, sorted_usernames)

    def test_build_base_search_queryset_wrapper(self):
        """Test that build_base_search_queryset properly wraps the privacy-aware function."""
        # Both functions should return the same results
        queryset1 = build_privacy_aware_search_queryset("john", self.user1)
        queryset2 = build_base_search_queryset("john", self.user1)

        self.assertEqual(list(queryset1), list(queryset2))

    def test_search_with_authenticated_user(self):
        """Test search with authenticated user (requesting_user parameter)."""
        # The function should work the same regardless of requesting_user
        # since it only builds the base queryset, not apply privacy filters
        queryset1 = build_privacy_aware_search_queryset("john", None)
        queryset2 = build_privacy_aware_search_queryset("john", self.user2)

        self.assertEqual(list(queryset1), list(queryset2))
