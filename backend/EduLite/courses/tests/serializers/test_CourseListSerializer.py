from datetime import datetime
from unittest.mock import MagicMock

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
        cls.outsider = User.objects.create_user(
            username="outsider", password="pass12345", email="outsider@example.com"
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

    def _get_context(self, user=None):
        """Build a serializer context with a mock request for the given user."""
        request = MagicMock()
        if user:
            request.user = user
        else:
            request.user = MagicMock(is_authenticated=False)
        return {"request": request}

    def test_list_serializer_contains_expected_fields(self):
        """Test that list serializer includes exactly the expected fields."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.user1)
        )
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
            "is_member",
            "user_role",
            "user_status",
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
        """Test that list serializer does not include members or modules."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.user1)
        )
        self.assertNotIn("members", serializer.data)
        self.assertNotIn("modules", serializer.data)
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

    # --- user_role tests ---

    def test_list_serializer_user_role_for_teacher(self):
        """Test that user_role returns 'teacher' for a teacher member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.user1)
        )
        self.assertEqual(serializer.data["user_role"], "teacher")

    def test_list_serializer_user_role_for_student(self):
        """Test that user_role returns 'student' for a student member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.user2)
        )
        self.assertEqual(serializer.data["user_role"], "student")

    def test_list_serializer_user_role_for_non_member(self):
        """Test that user_role returns null for a non-member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.outsider)
        )
        self.assertIsNone(serializer.data["user_role"])

    def test_list_serializer_user_role_unauthenticated(self):
        """Test that user_role returns null for an unauthenticated request."""
        serializer = CourseListSerializer(self.course, context=self._get_context())
        self.assertIsNone(serializer.data["user_role"])

    # --- user_status tests ---

    def test_list_serializer_user_status_for_enrolled(self):
        """Test that user_status returns 'enrolled' for an enrolled member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.user1)
        )
        self.assertEqual(serializer.data["user_status"], "enrolled")

    def test_list_serializer_user_status_for_invited(self):
        """Test that user_status returns 'invited' for an invited user."""
        invited_user = User.objects.create_user(
            username="invited_user", password="pass12345", email="invited@example.com"
        )
        CourseMembership.objects.create(
            user=invited_user, course=self.course, role="student", status="invited"
        )
        serializer = CourseListSerializer(
            self.course, context=self._get_context(invited_user)
        )
        self.assertEqual(serializer.data["user_status"], "invited")

    def test_list_serializer_user_status_for_pending(self):
        """Test that user_status returns 'pending' for a pending user."""
        pending_user = User.objects.create_user(
            username="pending_user", password="pass12345", email="pending@example.com"
        )
        CourseMembership.objects.create(
            user=pending_user, course=self.course, role="student", status="pending"
        )
        serializer = CourseListSerializer(
            self.course, context=self._get_context(pending_user)
        )
        self.assertEqual(serializer.data["user_status"], "pending")

    def test_list_serializer_user_status_for_non_member(self):
        """Test that user_status returns null for a non-member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.outsider)
        )
        self.assertIsNone(serializer.data["user_status"])

    # --- is_member tests ---

    def test_list_serializer_is_member_true(self):
        """Test that is_member returns True for a course member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.user1)
        )
        self.assertTrue(serializer.data["is_member"])

    def test_list_serializer_is_member_false(self):
        """Test that is_member returns False for a non-member."""
        serializer = CourseListSerializer(
            self.course, context=self._get_context(self.outsider)
        )
        self.assertFalse(serializer.data["is_member"])

    def test_list_serializer_is_member_unauthenticated(self):
        """Test that is_member returns False for an unauthenticated request."""
        serializer = CourseListSerializer(self.course, context=self._get_context())
        self.assertFalse(serializer.data["is_member"])
