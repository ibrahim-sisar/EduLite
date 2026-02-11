"""Tests for the course list API endpoint."""

from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership


class CourseListAPITests(APITestCase):
    """Validate GET /api/courses/ behaviour."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()
        cls.url = reverse("course-list-create")

        cls.teacher = cls._make_user("teacher_user", "teacher")
        cls.student = cls._make_user("student_user", "student")
        cls.outsider = cls._make_user("outsider_user", "student")

        # Public course — visible to everyone
        cls.public_course = Course.objects.create(
            title="Public Physics",
            visibility="public",
            subject="physics",
            language="en",
            country="US",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.public_course,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
        )
        CourseMembership.objects.create(
            course=cls.public_course,
            user=cls.student,
            role="student",
            status="enrolled",
        )

        # Private course — only visible to members
        cls.private_course = Course.objects.create(
            title="Private Math",
            visibility="private",
            subject="mathematics",
            language="fr",
            country="FR",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.private_course,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
        )

        # Restricted course — only visible to members
        cls.restricted_course = Course.objects.create(
            title="Restricted Chemistry",
            visibility="restricted",
            subject="chemistry",
            language="en",
            country="GB",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.restricted_course,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
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

    # --- Basic list behaviour ---

    def test_list_returns_paginated_shape(self):
        """Response has the expected pagination keys."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in ("count", "results", "total_pages", "current_page", "page_size"):
            self.assertIn(key, response.data)

    def test_public_courses_visible_to_all_authenticated(self):
        """An outsider (non-member) can see public courses."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(self.url)

        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Public Physics", titles)

    def test_private_courses_hidden_from_non_members(self):
        """An outsider cannot see private or restricted courses."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(self.url)

        titles = [c["title"] for c in response.data["results"]]
        self.assertNotIn("Private Math", titles)
        self.assertNotIn("Restricted Chemistry", titles)

    def test_private_courses_visible_to_members(self):
        """A member can see private courses they belong to."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url)

        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Private Math", titles)
        self.assertIn("Restricted Chemistry", titles)

    def test_unauthenticated_returns_401(self):
        """Unauthenticated users cannot list courses."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Filters ---

    def test_filter_by_visibility(self):
        """Filtering by visibility returns only matching courses."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url, {"visibility": "public"})

        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Public Physics", titles)
        self.assertNotIn("Private Math", titles)
        self.assertNotIn("Restricted Chemistry", titles)

    def test_filter_by_subject(self):
        """Filtering by subject returns only matching courses."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url, {"subject": "mathematics"})

        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Private Math", titles)
        self.assertNotIn("Public Physics", titles)

    def test_filter_by_language(self):
        """Filtering by language returns only matching courses."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url, {"language": "fr"})

        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Private Math", titles)
        self.assertNotIn("Public Physics", titles)

    def test_filter_by_country(self):
        """Filtering by country returns only matching courses."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url, {"country": "GB"})

        titles = [c["title"] for c in response.data["results"]]
        self.assertIn("Restricted Chemistry", titles)
        self.assertNotIn("Public Physics", titles)

    def test_filter_mine(self):
        """Filtering mine=true returns only the user's courses."""
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.url, {"mine": "true"})

        titles = [c["title"] for c in response.data["results"]]
        # Student is only a member of the public course
        self.assertIn("Public Physics", titles)
        self.assertEqual(len(titles), 1)

    # --- Annotation ---

    def test_member_count_is_correct(self):
        """The member_count field reflects enrolled members."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url, {"visibility": "public"})

        public = next(
            c for c in response.data["results"] if c["title"] == "Public Physics"
        )
        # teacher + student = 2 enrolled members
        self.assertEqual(public["member_count"], 2)
