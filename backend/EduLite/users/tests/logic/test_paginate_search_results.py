# users/tests/logic/test_paginate_search_results.py

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from users.logic.user_search_logic import paginate_search_results
from users.tests.fixtures.bulk_test_users import create_bulk_test_users


class PaginateSearchResultsTest(TestCase):
    """Test the paginate_search_results function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create many users for pagination testing
        cls.users = create_bulk_test_users("paginate", 25)

        # Create a mock view instance
        class MockView(APIView):
            pass

        cls.mock_view = MockView()

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()

    def test_paginate_with_default_page_size(self):
        """Test pagination with default page size."""
        # Create request
        request = self.api_factory.get("/api/users/search/", {"q": "test"})

        # Get queryset
        queryset = User.objects.all().order_by("id")

        # Paginate
        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        self.assertIsNotNone(paginator)
        self.assertEqual(paginator.page_size, 10)

        # Get the actual page data
        page = paginator.page
        self.assertEqual(len(page), 10)

    def test_paginate_with_custom_page_size(self):
        """Test pagination with custom page size."""
        request = self.api_factory.get("/api/users/search/", {"q": "test"})

        queryset = User.objects.all().order_by("id")

        # Use custom page size of 5
        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=5
        )

        self.assertIsNotNone(paginator)
        self.assertEqual(paginator.page_size, 5)

        page = paginator.page
        self.assertEqual(len(page), 5)

    def test_paginate_specific_page(self):
        """Test requesting a specific page."""
        # Request page 2
        request = self.api_factory.get("/api/users/search/", {"q": "test", "page": "2"})

        queryset = User.objects.all().order_by("id")

        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        self.assertIsNotNone(paginator)
        # Page 2 should have different users than page 1
        page = paginator.page
        self.assertLessEqual(len(page), 10)

    def test_paginate_last_page(self):
        """Test pagination on the last page with fewer items."""
        # With 25 users and page_size=10, page 3 should have 5 users
        request = self.api_factory.get("/api/users/search/", {"q": "test", "page": "3"})

        queryset = User.objects.all().order_by("id")

        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        self.assertIsNotNone(paginator)
        page = paginator.page
        expected_count = User.objects.count() % 10 or 10
        self.assertEqual(len(page), expected_count)

    def test_paginate_with_django_http_request(self):
        """Test pagination with Django HttpRequest (not DRF Request)."""
        # Use Django's RequestFactory
        request = self.factory.get("/api/users/search/", {"q": "test"})

        queryset = User.objects.all().order_by("id")

        # Should handle Django HttpRequest by wrapping it
        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        self.assertIsNotNone(paginator)
        page = paginator.page
        self.assertEqual(len(page), 10)

    def test_paginate_empty_queryset(self):
        """Test pagination with empty queryset."""
        request = self.api_factory.get("/api/users/search/", {"q": "test"})

        # Empty queryset
        queryset = User.objects.none()

        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        self.assertIsNotNone(paginator)
        page = paginator.page
        self.assertEqual(len(page), 0)

    def test_paginate_single_item(self):
        """Test pagination with single item."""
        request = self.api_factory.get("/api/users/search/", {"q": "test"})

        # Queryset with single user
        queryset = User.objects.filter(id=self.users[0].id)

        page_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        self.assertIsNotNone(paginator)
        page = paginator.page
        self.assertEqual(len(page), 1)

    def test_paginate_invalid_page_number(self):
        """Test pagination with invalid page number."""
        # Request page 999 (doesn't exist)
        request = self.api_factory.get(
            "/api/users/search/", {"q": "test", "page": "999"}
        )

        queryset = User.objects.all().order_by("id")

        # Should raise NotFound exception (DRF behavior)
        from rest_framework.exceptions import NotFound

        with self.assertRaises(NotFound):
            paginate_search_results(queryset, request, self.mock_view, page_size=10)

    def test_paginate_with_non_numeric_page(self):
        """Test pagination with non-numeric page parameter."""
        request = self.api_factory.get(
            "/api/users/search/", {"q": "test", "page": "abc"}
        )

        queryset = User.objects.all().order_by("id")

        # Should raise NotFound exception (DRF behavior)
        from rest_framework.exceptions import NotFound

        with self.assertRaises(NotFound):
            paginate_search_results(queryset, request, self.mock_view, page_size=10)

    def test_original_queryset_returned(self):
        """Test that original queryset is returned along with paginator."""
        request = self.api_factory.get("/api/users/search/", {"q": "test"})

        queryset = User.objects.all().order_by("id")

        returned_qs, paginator = paginate_search_results(
            queryset, request, self.mock_view, page_size=10
        )

        # The returned queryset should be the original one
        self.assertEqual(returned_qs.query.__str__(), queryset.query.__str__())

    def test_page_size_limits(self):
        """Test various page sizes."""
        request = self.api_factory.get("/api/users/search/", {"q": "test"})

        queryset = User.objects.all().order_by("id")

        # Test different page sizes
        for page_size in [1, 5, 20, 100]:
            page_qs, paginator = paginate_search_results(
                queryset, request, self.mock_view, page_size=page_size
            )

            self.assertEqual(paginator.page_size, page_size)
            page = paginator.page
            self.assertLessEqual(len(page), page_size)
