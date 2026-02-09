"""Tests for the course module CRUD API endpoints."""

from datetime import datetime
from typing import Optional

from chat.models import ChatRoom
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership, CourseModule


class CourseModuleAPITests(APITestCase):
    """Validate course module list/create/detail/update/delete behaviour."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        # Create users
        cls.teacher = cls._make_user("teacher_user", "teacher")
        cls.student = cls._make_user("student_user", "student")
        cls.outsider = cls._make_user("outsider_user", "student")

        # Create course
        cls.course = Course.objects.create(
            title="Test Course",
            outline="A course for testing modules.",
            language="en",
            country="US",
            subject="physics",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )

        # Enroll teacher and student
        CourseMembership.objects.create(
            course=cls.course, user=cls.teacher, role="teacher", status="enrolled"
        )
        CourseMembership.objects.create(
            course=cls.course, user=cls.student, role="student", status="enrolled"
        )

        # Content object for modules
        cls.chatroom = ChatRoom.objects.create(
            name="test_chatroom", room_type="ONE_TO_ONE"
        )
        cls.chatroom2 = ChatRoom.objects.create(
            name="test_chatroom2", room_type="ONE_TO_ONE"
        )
        cls.chatroom_ct = ContentType.objects.get_for_model(ChatRoom)

        # Pre-existing modules
        cls.module1 = CourseModule.objects.create(
            course=cls.course,
            title="Module A",
            order=1,
            content_type=cls.chatroom_ct,
            object_id=cls.chatroom.id,
        )
        cls.module2 = CourseModule.objects.create(
            course=cls.course,
            title="Module B",
            order=2,
            content_type=cls.chatroom_ct,
            object_id=cls.chatroom2.id,
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

    def _list_url(self):
        return reverse("course-module-list-create", kwargs={"pk": self.course.pk})

    def _detail_url(self, module_id):
        return reverse(
            "course-module-detail",
            kwargs={"pk": self.course.pk, "module_id": module_id},
        )

    # --- List (GET) ---

    def test_list_modules_as_member(self):
        """Enrolled members can list modules, ordered by order field."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Module A")
        self.assertEqual(response.data[1]["title"], "Module B")

    def test_list_modules_as_non_member(self):
        """Non-members are denied access to module listing."""
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(self._list_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_modules_unauthenticated(self):
        """Unauthenticated clients are rejected."""
        response = self.client.get(self._list_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Create (POST) ---

    def test_create_module_as_teacher(self):
        """Teachers can create modules in their course."""
        self.client.force_authenticate(user=self.teacher)
        payload = {
            "title": "New Module",
            "order": 3,
            "content_type": "chat.chatroom",
            "object_id": self.chatroom.id,
        }

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Module")
        self.assertEqual(response.data["order"], 3)
        self.assertEqual(response.data["course"], self.course.pk)
        self.assertTrue(
            CourseModule.objects.filter(course=self.course, title="New Module").exists()
        )

    def test_create_module_as_student(self):
        """Students cannot create modules."""
        self.client.force_authenticate(user=self.student)
        payload = {
            "title": "Sneaky Module",
            "order": 3,
            "content_type": "chat.chatroom",
            "object_id": self.chatroom.id,
        }

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_module_invalid_content_type(self):
        """Invalid content_type returns 400."""
        self.client.force_authenticate(user=self.teacher)
        payload = {
            "title": "Bad Module",
            "order": 3,
            "content_type": "invalid.model",
            "object_id": self.chatroom.id,
        }

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content_type", response.data)

    # --- Retrieve (GET detail) ---

    def test_retrieve_module_as_member(self):
        """Enrolled members can retrieve a single module."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._detail_url(self.module1.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Module A")
        self.assertEqual(response.data["id"], self.module1.pk)

    def test_retrieve_module_as_non_member(self):
        """Non-members cannot retrieve a module."""
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(self._detail_url(self.module1.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_module_not_found(self):
        """Requesting a non-existent module returns 404."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._detail_url(99999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Update (PATCH) ---

    def test_update_module_as_teacher(self):
        """Teachers can partially update a module."""
        self.client.force_authenticate(user=self.teacher)
        payload = {"title": "Updated Module A", "order": 10}

        response = self.client.patch(
            self._detail_url(self.module1.pk), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Module A")
        self.assertEqual(response.data["order"], 10)

    def test_update_module_as_student(self):
        """Students cannot update modules."""
        self.client.force_authenticate(user=self.student)
        payload = {"title": "Hacked Title"}

        response = self.client.patch(
            self._detail_url(self.module1.pk), payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Delete (DELETE) ---

    def test_delete_module_as_teacher(self):
        """Teachers can delete a module."""
        self.client.force_authenticate(user=self.teacher)

        # Create a throwaway module to delete
        module = CourseModule.objects.create(
            course=self.course,
            title="To Delete",
            order=99,
            content_type=self.chatroom_ct,
            object_id=self.chatroom.id,
        )

        response = self.client.delete(self._detail_url(module.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseModule.objects.filter(pk=module.pk).exists())

    def test_delete_module_as_student(self):
        """Students cannot delete modules."""
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self._detail_url(self.module1.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CourseModule.objects.filter(pk=self.module1.pk).exists())
