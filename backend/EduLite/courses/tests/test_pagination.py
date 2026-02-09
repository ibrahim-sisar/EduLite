from datetime import datetime

from django.test import TestCase, RequestFactory
from rest_framework.request import Request

from ..models import Course
from ..pagination import CoursePagination


class CoursePaginationTest(TestCase):
    """Test suite for CoursePagination."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        # Create 25 courses for pagination testing
        courses = []
        for i in range(25):
            courses.append(
                Course(
                    title=f"Course {i}",
                    outline=f"Outline for course {i}",
                    visibility="public",
                    start_date=datetime(2025, 1, 1),
                    end_date=datetime(2025, 12, 31),
                )
            )
        Course.objects.bulk_create(courses)

    def _paginate(self, query_params=""):
        """Helper to paginate the full Course queryset with given query params."""
        paginator = CoursePagination()
        django_request = self.factory.get(f"/?{query_params}" if query_params else "/")
        request = Request(django_request)
        queryset = Course.objects.all().order_by("id")
        page = paginator.paginate_queryset(queryset, request)
        response = paginator.get_paginated_response(
            [{"id": c.id, "title": c.title} for c in page]
        )
        return response.data

    def test_pagination_response_structure(self):
        """Test that paginated response contains all expected keys."""
        data = self._paginate()
        expected_keys = {
            "next",
            "previous",
            "count",
            "total_pages",
            "current_page",
            "results",
            "page_size",
        }
        self.assertEqual(set(data.keys()), expected_keys)

    def test_pagination_default_page_size(self):
        """Test that default page size is 20."""
        data = self._paginate()
        self.assertEqual(data["page_size"], 20)
        self.assertEqual(len(data["results"]), 20)
        self.assertEqual(data["count"], 25)
        self.assertEqual(data["total_pages"], 2)
        self.assertEqual(data["current_page"], 1)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])

    def test_pagination_custom_page_size(self):
        """Test that custom page_size query parameter works."""
        data = self._paginate("page_size=10")
        self.assertEqual(data["page_size"], 10)
        self.assertEqual(len(data["results"]), 10)
        self.assertEqual(data["count"], 25)
        self.assertEqual(data["total_pages"], 3)

    def test_pagination_max_page_size(self):
        """Test that page_size is capped at max_page_size (100)."""
        data = self._paginate("page_size=200")
        self.assertEqual(data["page_size"], 100)
        # All 25 courses fit in one page when max is 100
        self.assertEqual(len(data["results"]), 25)
        self.assertEqual(data["total_pages"], 1)

    def test_pagination_second_page(self):
        """Test navigating to second page."""
        data = self._paginate("page=2")
        self.assertEqual(data["current_page"], 2)
        self.assertEqual(len(data["results"]), 5)  # 25 - 20 = 5 remaining
        self.assertIsNone(data["next"])
        self.assertIsNotNone(data["previous"])
