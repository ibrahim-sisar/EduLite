# courses/tests/test_CourseMembership.py
# Tests for the CourseMembership model

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Course, CourseMembership

User = get_user_model()


class CourseMembershipTest(TestCase):
    """
    Unit tests for the CourseMembership model.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Set up reusable test data for Course and Users.
        """
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

    def test_course_membership_creation(self) -> None:
        """
        Test that a CourseMembership is successfully created.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user2,
            course=self.course1,
            role="student",
        )
        course_membership.full_clean()
        self.assertEqual(course_membership.user, self.user2)
        self.assertEqual(course_membership.course, self.course1)

    def test_course_membership_str(self) -> None:
        """
        Test string representation of CourseMembership.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        expected_str = f"{self.user1.username} - {self.course1.title} - student"
        self.assertEqual(str(course_membership), expected_str)

    def test_course_membership_role(self) -> None:
        """
        Test that the role field is stored correctly.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        self.assertEqual(course_membership.role, "student")

    def test_course_membership_delete(self) -> None:
        """
        Test that a CourseMembership is deleted properly.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        membership_id = course_membership.id
        course_membership.delete()
        self.assertFalse(CourseMembership.objects.filter(pk=membership_id).exists())

    def test_course_membership_update(self) -> None:
        """
        Test that updating role field works as expected.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        course_membership.role = "teacher"
        course_membership.save()
        course_membership.refresh_from_db()
        self.assertEqual(course_membership.role, "teacher")

    def test_course_membership_default_status(self) -> None:
        """
        Test that default status is set to 'enrolled'.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        self.assertEqual(course_membership.status, "enrolled")

    def test_course_membership_with_invalid_status(self) -> None:
        """
        Test that a teacher cannot have a 'pending' status.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="teacher",
            status="pending",
        )
        with self.assertRaises(ValidationError):
            course_membership.full_clean()

    def test_course_membership_clean_duplicate_membership(self) -> None:
        """
        Test that duplicate user-course membership raises ValidationError.
        """
        CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        duplicate = CourseMembership(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_invalid_role_choice(self) -> None:
        """
        Test that an invalid role value raises ValidationError.
        """
        course_membership = CourseMembership(
            user=self.user1,
            course=self.course1,
            role="invalid_role",
        )
        with self.assertRaises(ValidationError):
            course_membership.full_clean()

    def test_user_delete_cascade(self) -> None:
        """
        Test that deleting a user deletes their course memberships.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        membership_id = course_membership.id
        self.user1.delete()
        self.assertFalse(CourseMembership.objects.filter(pk=membership_id).exists())

    def test_course_delete_cascade(self) -> None:
        """
        Test that deleting a course deletes its memberships.
        """
        course_membership = CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        membership_id = course_membership.id
        self.course1.delete()
        self.assertFalse(CourseMembership.objects.filter(pk=membership_id).exists())

    def test_clean_with_unsaved_course_does_not_crash(self) -> None:
        """
        Test that clean() does not crash when the course is unsaved (no PK).
        This happens when creating a course with an inline membership in admin.
        """
        unsaved_course = Course(title="Unsaved Course")
        membership = CourseMembership(
            user=self.user1,
            course=unsaved_course,
            role="teacher",
            status="enrolled",
        )
        # Should not raise ValueError about unsaved model instances
        membership.clean()

    def test_clean_with_unsaved_user_does_not_crash(self) -> None:
        """
        Test that clean() does not crash when the user is unsaved (no PK).
        """
        unsaved_user = User(username="unsaved", email="unsaved@example.com")
        membership = CourseMembership(
            user=unsaved_user,
            course=self.course1,
            role="student",
            status="enrolled",
        )
        # Should not raise ValueError about unsaved model instances
        membership.clean()

    def test_clean_still_catches_duplicates_when_saved(self) -> None:
        """
        Test that clean() still catches duplicate memberships when both
        user and course are saved (have PKs).
        """
        CourseMembership.objects.create(
            user=self.user1,
            course=self.course1,
            role="student",
        )
        duplicate = CourseMembership(
            user=self.user1,
            course=self.course1,
            role="teacher",
        )
        with self.assertRaises(ValidationError):
            duplicate.clean()
