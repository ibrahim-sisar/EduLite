# users/tests/logic/test_validate_search_query.py

from django.test import TestCase
from rest_framework import status

from users.logic.user_search_logic import validate_search_query


class ValidateSearchQueryTest(TestCase):
    """Test the validate_search_query function."""

    def test_empty_query_returns_error(self):
        """Test that empty query returns validation error."""
        is_valid, error_response = validate_search_query("")

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_response.data["detail"], "Search query is required.")

    def test_none_query_returns_error(self):
        """Test that None query returns validation error."""
        is_valid, error_response = validate_search_query(None)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_response.data["detail"], "Search query is required.")

    def test_whitespace_only_query_returns_error(self):
        """Test that whitespace-only query returns validation error."""
        is_valid, error_response = validate_search_query("   ")

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_response.data["detail"], "Search query is required.")

    def test_query_below_minimum_length_returns_error(self):
        """Test that query below minimum length returns validation error."""
        is_valid, error_response = validate_search_query("a")

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_response)
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            error_response.data["detail"],
            "Search query must be at least 2 characters long.",
        )

    def test_query_exactly_minimum_length_is_valid(self):
        """Test that query exactly at minimum length is valid."""
        is_valid, error_response = validate_search_query("ab")

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_longer_query_is_valid(self):
        """Test that longer query is valid."""
        is_valid, error_response = validate_search_query("test user")

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_query_with_leading_trailing_spaces_is_valid(self):
        """Test that query with spaces is trimmed and validated."""
        is_valid, error_response = validate_search_query("  test  ")

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_custom_minimum_length(self):
        """Test validation with custom minimum length."""
        # Test with min_length=3
        is_valid, error_response = validate_search_query("ab", min_length=3)

        self.assertFalse(is_valid)
        self.assertIsNotNone(error_response)
        self.assertEqual(
            error_response.data["detail"],
            "Search query must be at least 3 characters long.",
        )

        # Test valid with min_length=3
        is_valid, error_response = validate_search_query("abc", min_length=3)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_single_character_with_min_length_1(self):
        """Test that single character is valid when min_length=1."""
        is_valid, error_response = validate_search_query("a", min_length=1)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

    def test_unicode_characters_count_correctly(self):
        """Test that unicode characters are counted correctly."""
        # Test with emoji (should count as valid characters)
        is_valid, error_response = validate_search_query("👋🏼", min_length=2)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)

        # Test with Arabic characters
        is_valid, error_response = validate_search_query("أحمد", min_length=4)

        self.assertTrue(is_valid)
        self.assertIsNone(error_response)
