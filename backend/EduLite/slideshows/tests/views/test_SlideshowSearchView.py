"""Tests for SlideshowSearchView."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_mercury import monitor
from rest_framework import status
from rest_framework.test import APIClient

from slideshows.models import Slideshow

User = get_user_model()


class SlideshowSearchViewTestCase(TestCase):
    """Test cases for slideshow search endpoint."""

    @classmethod
    def setUpTestData(cls):
        """Create test data once for all tests."""
        cls.user = User.objects.create_user(
            username="searcher", email="searcher@test.com", password="password123"
        )
        cls.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="password123"
        )

        # User's own slideshows (various visibility/published states)
        cls.own_public_published = Slideshow.objects.create(
            title="My Python Basics",
            description="Learn Python fundamentals",
            created_by=cls.user,
            visibility="public",
            is_published=True,
            subject="computer_science",
        )
        cls.own_private = Slideshow.objects.create(
            title="My Private Notes",
            description="Personal study notes on Python",
            created_by=cls.user,
            visibility="private",
            is_published=True,
        )
        cls.own_unpublished = Slideshow.objects.create(
            title="My Draft Python Course",
            description="Work in progress",
            created_by=cls.user,
            visibility="public",
            is_published=False,
        )
        cls.own_unlisted = Slideshow.objects.create(
            title="My Unlisted Python Guide",
            description="Unlisted slideshow",
            created_by=cls.user,
            visibility="unlisted",
            is_published=True,
        )

        # Other user's slideshows
        cls.other_public_published = Slideshow.objects.create(
            title="Advanced Python Patterns",
            description="Design patterns in Python",
            created_by=cls.other_user,
            visibility="public",
            is_published=True,
            subject="computer_science",
        )
        cls.other_private = Slideshow.objects.create(
            title="Secret Python Tips",
            description="Private collection of Python tricks",
            created_by=cls.other_user,
            visibility="private",
            is_published=True,
        )
        cls.other_unlisted = Slideshow.objects.create(
            title="Unlisted Python Workshop",
            description="Hidden Python workshop slides",
            created_by=cls.other_user,
            visibility="unlisted",
            is_published=True,
        )
        cls.other_unpublished = Slideshow.objects.create(
            title="Unpublished Python Draft",
            description="Not ready yet",
            created_by=cls.other_user,
            visibility="public",
            is_published=False,
        )

        # Slideshow with no Python in title/description (for negative match)
        cls.unrelated = Slideshow.objects.create(
            title="History of Mathematics",
            description="From ancient times to modern day",
            created_by=cls.other_user,
            visibility="public",
            is_published=True,
            subject="mathematics",
        )

        cls.url = reverse("slideshows:slideshow-search")

    def setUp(self):
        """Set up test client for each test."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # --- Authentication ---

    def test_unauthenticated_returns_401(self):
        """Unauthenticated requests should return 401."""
        self.client.logout()
        response = self.client.get(self.url, {"q": "Python"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Query Validation ---

    def test_no_query_returns_400(self):
        """Missing query parameter should return 400."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_empty_query_returns_400(self):
        """Empty query string should return 400."""
        response = self.client.get(self.url, {"q": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_whitespace_query_returns_400(self):
        """Whitespace-only query should return 400."""
        response = self.client.get(self.url, {"q": "   "})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_single_char_query_returns_400(self):
        """Single character query should return 400."""
        response = self.client.get(self.url, {"q": "P"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("at least 2 characters", response.data["detail"])

    def test_two_char_query_succeeds(self):
        """Two character query should succeed."""
        response = self.client.get(self.url, {"q": "Py"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Title Search ---

    def test_search_matches_title(self):
        """Should find slideshows matching title."""
        with monitor(response_time_ms=100, query_count=5):
            response = self.client.get(self.url, {"q": "Python Basics"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Python Basics", titles)

    def test_search_partial_title_match(self):
        """Should find slideshows with partial title match."""
        response = self.client.get(self.url, {"q": "Basics"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Python Basics", titles)

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        response = self.client.get(self.url, {"q": "python basics"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Python Basics", titles)

    # --- Description Search ---

    def test_search_matches_description(self):
        """Should find slideshows matching description."""
        response = self.client.get(self.url, {"q": "fundamentals"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Python Basics", titles)

    def test_search_description_case_insensitive(self):
        """Description search should be case-insensitive."""
        response = self.client.get(self.url, {"q": "DESIGN PATTERNS"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("Advanced Python Patterns", titles)

    # --- No Results ---

    def test_no_results_returns_empty_list(self):
        """Query with no matches should return empty results, not 404."""
        response = self.client.get(self.url, {"q": "xyznonexistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    # --- Visibility Rules ---

    def test_user_sees_own_private_slideshows(self):
        """User should see their own private slideshows in search results."""
        response = self.client.get(self.url, {"q": "Private Notes"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Private Notes", titles)

    def test_user_sees_own_unpublished_slideshows(self):
        """User should see their own unpublished slideshows in search results."""
        response = self.client.get(self.url, {"q": "Draft Python"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Draft Python Course", titles)

    def test_user_sees_own_unlisted_slideshows(self):
        """User should see their own unlisted slideshows in search results."""
        response = self.client.get(self.url, {"q": "Unlisted Python Guide"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("My Unlisted Python Guide", titles)

    def test_user_sees_others_public_published(self):
        """User should see others' public published slideshows."""
        response = self.client.get(self.url, {"q": "Advanced Python"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertIn("Advanced Python Patterns", titles)

    def test_user_does_not_see_others_private(self):
        """User should NOT see others' private slideshows."""
        response = self.client.get(self.url, {"q": "Secret Python"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertNotIn("Secret Python Tips", titles)

    def test_user_does_not_see_others_unlisted(self):
        """User should NOT see others' unlisted slideshows."""
        response = self.client.get(self.url, {"q": "Unlisted Python Workshop"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertNotIn("Unlisted Python Workshop", titles)

    def test_user_does_not_see_others_unpublished(self):
        """User should NOT see others' unpublished slideshows."""
        response = self.client.get(self.url, {"q": "Unpublished Python"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in response.data["results"]]
        self.assertNotIn("Unpublished Python Draft", titles)

    # --- Combined Filters ---

    def test_search_with_subject_filter(self):
        """Search combined with subject filter should narrow results."""
        # Search "Python" with subject=computer_science
        response = self.client.get(
            self.url, {"q": "Python", "subject": "computer_science"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data["results"]:
            self.assertEqual(result["subject"], "computer_science")

    def test_search_with_mine_filter(self):
        """Search combined with mine=true should only return user's own slideshows."""
        response = self.client.get(self.url, {"q": "Python", "mine": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data["results"]:
            self.assertEqual(result["created_by"], self.user.pk)

    def test_search_with_visibility_filter(self):
        """Search combined with visibility filter should narrow results."""
        response = self.client.get(self.url, {"q": "Python", "visibility": "private"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data["results"]:
            self.assertEqual(result["visibility"], "private")

    # --- Pagination ---

    def test_results_are_paginated(self):
        """Search results should include pagination fields."""
        response = self.client.get(self.url, {"q": "Python"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("current_page", response.data)

    def test_custom_page_size(self):
        """Custom page_size parameter should be respected."""
        response = self.client.get(self.url, {"q": "Python", "page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]), 2)

    def test_pagination_with_many_results(self):
        """Pagination should work correctly with many results."""
        # Create 25 slideshows to exceed default page size of 20
        for i in range(25):
            Slideshow.objects.create(
                title=f"Bulk Slideshow {i}",
                description="Bulk test slideshow",
                created_by=self.user,
                visibility="public",
                is_published=True,
            )

        response = self.client.get(self.url, {"q": "Bulk Slideshow"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 20)  # default page_size
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    # --- Response Format ---

    def test_response_uses_list_serializer_fields(self):
        """Response results should contain SlideshowListSerializer fields."""
        response = self.client.get(self.url, {"q": "Python Basics"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["results"]), 0)

        result = response.data["results"][0]
        expected_fields = [
            "id",
            "title",
            "description",
            "created_by",
            "created_by_username",
            "visibility",
            "is_published",
            "slide_count",
            "created_at",
            "updated_at",
        ]
        for field in expected_fields:
            self.assertIn(field, result)
