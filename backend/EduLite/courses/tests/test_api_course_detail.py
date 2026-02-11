"""Tests for the course detail (GET/PATCH/DELETE) API endpoint."""

from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership


class CourseDetailAPITests(APITestCase):
    """Validate GET, PATCH, DELETE on /api/courses/<pk>/."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        cls.teacher = cls._make_user("teacher_user", "teacher")
        cls.student = cls._make_user("student_user", "student")
        cls.outsider = cls._make_user("outsider_user", "student")

        cls.course = Course.objects.create(
            title="Test Course",
            outline="A course for testing.",
            language="en",
            country="US",
            subject="physics",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )

        cls.teacher_membership = CourseMembership.objects.create(
            course=cls.course, user=cls.teacher, role="teacher", status="enrolled"
        )
        cls.student_membership = CourseMembership.objects.create(
            course=cls.course, user=cls.student, role="student", status="enrolled"
        )

    @classmethod
    def _make_user(cls, username: str, occupation: Optional[str] = None):
        user = cls.user_model.objects.create_user(
            username=username, password="test-pass-123"
        )
        if occupation is not None:
            profile = user.profile
            profile.occupation = occupation
            profile.save()
        return user

    def _detail_url(self, course):
        return reverse("course-detail", kwargs={"pk": course.pk})

    # --- GET ---

    def test_teacher_can_retrieve_course(self):
        """A teacher can retrieve full course details."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Course")
        self.assertIn("members", response.data)
        self.assertIn("modules", response.data)
        self.assertEqual(response.data["user_role"], "teacher")

    def test_student_can_retrieve_course(self):
        """An enrolled student can retrieve course details."""
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_role"], "student")

    def test_non_member_cannot_retrieve_course(self):
        """A non-member cannot retrieve course details."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_retrieve_course(self):
        """Unauthenticated users cannot retrieve course details."""
        response = self.client.get(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- PATCH ---

    def test_teacher_can_update_course(self):
        """A teacher can partially update course fields."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            self._detail_url(self.course),
            {"title": "Updated Title", "outline": "New outline"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Title")
        self.assertEqual(response.data["outline"], "New outline")

        # Restore for other tests
        self.course.refresh_from_db()
        self.course.title = "Test Course"
        self.course.outline = "A course for testing."
        self.course.save()

    def test_student_cannot_update_course(self):
        """A student cannot update course fields."""
        self.client.force_authenticate(user=self.student)

        response = self.client.patch(
            self._detail_url(self.course),
            {"title": "Hacked Title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_member_cannot_update_course(self):
        """A non-member cannot update course fields."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.patch(
            self._detail_url(self.course),
            {"title": "Hacked Title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_update_course(self):
        """Unauthenticated users cannot update courses."""
        response = self.client.patch(
            self._detail_url(self.course),
            {"title": "Hacked Title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_blank_title_rejected(self):
        """A blank title is rejected with 400."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            self._detail_url(self.course),
            {"title": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_end_date_before_start_date_rejected(self):
        """Setting end_date before start_date is rejected with 400."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            self._detail_url(self.course),
            {"end_date": "2024-01-01T00:00:00Z"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- DELETE ---

    def test_teacher_can_delete_course(self):
        """A teacher can delete a course."""
        course = Course.objects.create(
            title="Deletable Course",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=course, user=self.teacher, role="teacher", status="enrolled"
        )
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(self._detail_url(course))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())

    def test_student_cannot_delete_course(self):
        """A student cannot delete a course."""
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_member_cannot_delete_course(self):
        """A non-member cannot delete a course."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.delete(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_delete_course(self):
        """Unauthenticated users cannot delete courses."""
        response = self.client.delete(self._detail_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- PUT ---

    def test_put_returns_405(self):
        """PUT is not allowed, returns 405."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.put(
            self._detail_url(self.course),
            {"title": "Full Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
