"""Tests for the course enrollment (join/leave) API endpoints."""

from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership


class CourseEnrollAPITests(APITestCase):
    """Validate POST (join) and DELETE (leave) on /api/courses/<pk>/enroll/."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        cls.teacher = cls._make_user("teacher_user", "teacher")
        cls.student = cls._make_user("student_user", "student")
        cls.outsider = cls._make_user("outsider_user", "student")

        # Public course
        cls.public_course = Course.objects.create(
            title="Public Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.public_course,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
        )

        # Restricted course with join requests
        cls.restricted_open = Course.objects.create(
            title="Restricted Open",
            visibility="restricted",
            allow_join_requests=True,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.restricted_open,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
        )

        # Restricted course without join requests
        cls.restricted_closed = Course.objects.create(
            title="Restricted Closed",
            visibility="restricted",
            allow_join_requests=False,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )

        # Private course
        cls.private_course = Course.objects.create(
            title="Private Course",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
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

    def _enroll_url(self, course):
        return reverse("course-enroll", kwargs={"pk": course.pk})

    # --- Join (POST) ---

    def test_join_public_course(self):
        """Joining a public course creates an enrolled membership."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "enrolled")
        self.assertEqual(response.data["role"], "student")

        # Cleanup
        CourseMembership.objects.filter(
            course=self.public_course, user=self.outsider
        ).delete()

    def test_join_restricted_with_join_requests(self):
        """Joining a restricted course with allow_join_requests creates a pending membership."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.restricted_open))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["role"], "student")

        # Cleanup
        CourseMembership.objects.filter(
            course=self.restricted_open, user=self.outsider
        ).delete()

    def test_join_restricted_without_join_requests(self):
        """Joining a restricted course without allow_join_requests is denied."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.restricted_closed))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_private_course(self):
        """Joining a private course is denied."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.private_course))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_already_member(self):
        """Joining a course you're already in returns 409."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_join_unauthenticated(self):
        """Unauthenticated users cannot join courses."""
        response = self.client.post(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Leave (DELETE) ---

    def test_leave_course(self):
        """A member can leave a course."""
        # Create a membership to leave
        membership = CourseMembership.objects.create(
            course=self.public_course,
            user=self.student,
            role="student",
            status="enrolled",
        )
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMembership.objects.filter(pk=membership.pk).exists())

    def test_last_teacher_cannot_leave(self):
        """The last teacher in a course cannot leave."""
        # Create a solo-teacher course
        solo_course = Course.objects.create(
            title="Solo Teacher Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=solo_course,
            user=self.teacher,
            role="teacher",
            status="enrolled",
        )
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(self._enroll_url(solo_course))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_non_member_leave(self):
        """Leaving a course you're not in returns 404."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.delete(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_leave_unauthenticated(self):
        """Unauthenticated users cannot leave courses."""
        response = self.client.delete(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
