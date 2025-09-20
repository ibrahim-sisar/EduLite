# backend/EduLite/courses/tests/serializers/test_CourseSerializer.py
# Tests for CourseSerializer

from datetime import datetime, timedelta
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from ...models import Course
from ...serializers import CourseSerializer


class CourseSerializerTest(TestCase):
    """Test suite for CourseSerializer."""

    @classmethod
    def setUpTestData(cls):
        """Set up a course instance for testing."""
        cls.course1 = Course.objects.create(
            title="test_course1",
            outline="This is test_course1 outline",
            language="en",
            country="US",
            subject="physics",
            visibility="public",
            start_date=datetime(2025, 12, 31, 23, 59, 59),
            end_date=datetime(2026, 1, 30, 23, 59, 59),
            is_active=False,
            allow_join_requests=False,
        )

    def test_serializer_contains_all_fields(self):
        """Ensure the serializer includes all expected fields."""
        serializer = CourseSerializer(instance=self.course1)
        data = serializer.data
        self.assertEqual(data["title"], "test_course1")
        self.assertEqual(data["outline"], "This is test_course1 outline")
        self.assertEqual(data["language"], "en")
        self.assertEqual(data["country"], "US")
        self.assertEqual(data["subject"], "physics")
        self.assertEqual(data["visibility"], "public")
        self.assertIn("duration_time", data)

    def test_serializer_get_duration_time(self):
        """Test the get_duration_time method with valid dates."""
        serializer = CourseSerializer(instance=self.course1)
        self.assertEqual(serializer.data["duration_time"], 43200)  # 30 days * 24 * 60

    def test_serializer_invalid_date(self):
        """Test serializer with invalid date range (start_date after end_date)."""
        payload = {
            "title": "test course",
            "outline": "outline",
            "language": "en",
            "country": "US",
            "subject": "math",
            "visibility": "public",
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2025-01-01T00:00:00Z",  # invalid
        }
        serializer = CourseSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("end_date", serializer.errors)

    def test_serializer_invalid_title(self):
        """Test serializer with title that is only whitespace."""
        payload = {
            "title": "   ",
            "outline": "outline",
            "language": "en",
            "country": "US",
            "subject": "math",
            "visibility": "public",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-12-31T00:00:00Z",
        }
        serializer = CourseSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
