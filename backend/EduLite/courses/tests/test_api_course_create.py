"""Tests for the course creation API endpoint."""

from datetime import timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership


class CourseCreateAPITests(APITestCase):
    """Validate POST /api/courses/ behaviour."""

    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("course-create")
        self.user_model = get_user_model()

    def _create_user(self, username: str, occupation: Optional[str] = None):
        user = self.user_model.objects.create_user(username=username, password="test-pass-123")
        if occupation is not None:
            profile = user.profile
            profile.occupation = occupation
            profile.save()
        return user

    def test_teacher_can_create_course(self):
        """Teachers can create courses and become course members automatically."""

        teacher = self._create_user("teacher_creator", "teacher")
        self.client.force_authenticate(user=teacher)

        start = timezone.now()
        end = start + timedelta(days=30)
        payload = {
            "title": "Quantum Mechanics 101",
            "outline": "An introduction to quantum principles.",
            "language": "en",
            "country": "US",
            "subject": "physics",
            "visibility": "private",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "allow_join_requests": True,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)

        course = Course.objects.get(pk=response.data["id"])
        self.assertEqual(course.title, payload["title"])
        self.assertTrue(course.allow_join_requests)
        self.assertTrue(
            CourseMembership.objects.filter(
                course=course, user=teacher, role="teacher", status="enrolled"
            ).exists()
        )

    def test_non_teacher_can_create_course_and_is_set_as_teacher(self):
        """Any authenticated user can create a course and becomes the teacher member."""

        student = self._create_user("student_user", "student")
        self.client.force_authenticate(user=student)

        response = self.client.post(
            self.url,
            {
                "title": "Course by student",
                "language": "en",
                "visibility": "private",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(pk=response.data["id"])
        self.assertTrue(
            CourseMembership.objects.filter(
                course=course, user=student, role="teacher", status="enrolled"
            ).exists()
        )

    def test_validation_errors_returned(self):
        """Serializer validation errors surface as 400 responses."""

        teacher = self._create_user("invalid_teacher", "teacher")
        self.client.force_authenticate(user=teacher)

        response = self.client.post(self.url, {"title": "   "}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(Course.objects.count(), 0)
        self.assertEqual(CourseMembership.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_course(self):
        """Unauthenticated clients are rejected with 401 errors."""

        response = self.client.post(
            self.url,
            {
                "title": "No Auth Course",
                "language": "en",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Course.objects.count(), 0)
        self.assertEqual(CourseMembership.objects.count(), 0)
