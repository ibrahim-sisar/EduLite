from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from ...models import Course, CourseMembership
from ...serializers import CourseListSerializer

User = get_user_model()


class CourseListSerializerTest(TestCase):
    """Test suite for CourseListSerializer."""

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="teacher1", password="pass12345", email="teacher1@example.com"
        )
        cls.user2 = User.objects.create_user(
            username="student1", password="pass12345", email="student1@example.com"
        )
        cls.course = Course.objects.create(
            title="Test Course",
            outline="A test course outline",
            language="en",
            country="US",
            subject="physics",
            visibility="public",
            start_date=datetime(2025, 9, 1, 8, 0, 0),
            end_date=datetime(2025, 12, 15, 20, 0, 0),
            is_active=True,
        )
        CourseMembership.objects.create(
            user=cls.user1, course=cls.course, role="teacher", status="enrolled"
        )
        CourseMembership.objects.create(
            user=cls.user2, course=cls.course, role="student", status="enrolled"
        )

    def test_list_serializer_contains_expected_fields(self):
        """Test that list serializer includes exactly the expected fields."""
        serializer = CourseListSerializer(self.course)
        expected_fields = {
            "id",
            "title",
            "outline",
            "visibility",
            "subject",
            "language",
            "country",
            "is_active",
            "member_count",
            "start_date",
            "end_date",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_list_serializer_member_count(self):
        """Test that member_count returns the correct number of memberships."""
        serializer = CourseListSerializer(self.course)
        self.assertEqual(serializer.data["member_count"], 2)

    def test_list_serializer_member_count_with_annotation(self):
        """Test that member_count reads from annotation when available."""
        from django.db.models import Count

        qs = Course.objects.annotate(member_count=Count("memberships"))
        course = qs.get(pk=self.course.pk)
        serializer = CourseListSerializer(course)
        self.assertEqual(serializer.data["member_count"], 2)

    def test_list_serializer_does_not_include_nested_data(self):
        """Test that list serializer does not include members, modules, or user_role."""
        serializer = CourseListSerializer(self.course)
        self.assertNotIn("members", serializer.data)
        self.assertNotIn("modules", serializer.data)
        self.assertNotIn("user_role", serializer.data)
        self.assertNotIn("duration_time", serializer.data)
        self.assertNotIn("allow_join_requests", serializer.data)

    def test_list_serializer_field_values(self):
        """Test that serialized field values match the model."""
        serializer = CourseListSerializer(self.course)
        data = serializer.data
        self.assertEqual(data["title"], "Test Course")
        self.assertEqual(data["outline"], "A test course outline")
        self.assertEqual(data["visibility"], "public")
        self.assertEqual(data["subject"], "physics")
        self.assertEqual(data["language"], "en")
        self.assertEqual(data["country"], "US")
        self.assertTrue(data["is_active"])
