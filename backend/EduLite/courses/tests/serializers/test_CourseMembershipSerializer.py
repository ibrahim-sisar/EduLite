# backend/EduLite/courses/tests/serializers/test_CourseMembershipSerializer.py
# Tests for CourseMembershipSerializer

from datetime import datetime
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ...models import CourseMembership, Course
from ...serializers import CourseMembershipSerializer

User = get_user_model()


class CourseMembershipSerializerTest(TestCase):
    """Test suite for CourseMembershipSerializer."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up user, course, and course membership instances for testing."""
        cls.user1 = User.objects.create_user(
            username="testuser1", password="password123", email="testuser1@example.com"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2", password="password123", email="testuser2@example.com"
        )
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
        cls.course_membership1 = CourseMembership.objects.create(
            user=cls.user1,
            course=cls.course1,
            role="student",
        )

    def test_serializer_contains_all_fields(self):
        """Ensure the serializer includes all expected fields."""
        serializer = CourseMembershipSerializer(instance=self.course_membership1)
        data = serializer.data
        self.assertEqual(data["id"], self.course_membership1.id)
        self.assertEqual(data["user"], self.course_membership1.user.id)
        self.assertEqual(data["course"], self.course_membership1.course.id)
        self.assertEqual(data["role"], self.course_membership1.role)
        self.assertEqual(data["course_title"], self.course_membership1.course.title)
        self.assertEqual(data["user_name"], self.course_membership1.user.username)

    def test_serializer_validation(self):
        """Test serializer validation logic."""
        payload = {
            "user": self.user2.id,
            "course": self.course_membership1.course.id,
            "role": "student",
        }
        serializer = CourseMembershipSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_user(self):
        """Test serializer with non-existent user."""
        payload = {
            "user": self.user1.id,
            "course": self.course_membership1.course.id,
            "role": "student",
        }
        serializer = CourseMembershipSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_serializer_invalid_role(self):
        """Test serializer with invalid status for the specified role."""
        payload = {
            "user": self.user2.id,
            "course": self.course1.id,
            "role": "teacher",
            "status": "pending",
        }
        serializer = CourseMembershipSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_student_pending_is_allowed(self):
        """Test that a student can have 'pending' status."""
        payload = {
            "user": self.user2.id,
            "course": self.course1.id,
            "role": "student",
            "status": "pending",
        }
        serializer = CourseMembershipSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_update_violates_uniqueness(self):
        """Test updating a CourseMembership to a user-course pair that already exists."""
        m2 = CourseMembership.objects.create(
            user=self.user2, course=self.course1, role="student"
        )
        payload = {"user": self.user1.id, "course": self.course1.id, "role": "student"}
        serializer = CourseMembershipSerializer(instance=m2, data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_missing_user_or_course(self):
        """Test serializer validation when user or course is missing."""
        serializer = CourseMembershipSerializer(data={"role": "student"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("user", serializer.errors)
        self.assertIn("course", serializer.errors)

    def test_readonly_derived_fields_ignored_on_input(self):
        """Test that read-only fields are ignored during creation."""
        payload = {
            "user": self.user2.id,
            "course": self.course1.id,
            "role": "student",
            "user_name": "hacker",
            "course_title": "fake",
        }
        serializer = CourseMembershipSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.user.username, self.user2.username)
        self.assertEqual(instance.course.title, self.course1.title)
