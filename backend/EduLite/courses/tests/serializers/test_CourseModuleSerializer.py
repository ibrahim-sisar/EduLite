# backend/EduLite/courses/tests/serializers/test_CourseModuleSerializer.py
# Tests for CourseModuleSerializer

from datetime import datetime
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ...models import CourseModule, Course
from chat.models import ChatRoom
from ...serializers import CourseModuleSerializer

User = get_user_model()


class CourseModuleSerializerTest(TestCase):
    """
    Test suite for CourseModuleSerializer.
    Focuses on content_type and object_id validation.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Set up course, chat room, and course module instances for testing.
        Pretends that ChatRoom is a valid content type for CourseModule.
        """
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
        cls.chat_room1 = ChatRoom.objects.create(
            name="test_chat_room1",
            room_type="ONE_TO_ONE",
        )
        chatroom_ct = ContentType.objects.get_for_model(ChatRoom)

        cls.course_module1 = CourseModule.objects.create(
            course=cls.course1,
            content_type=chatroom_ct,
            object_id=cls.chat_room1.id,
            title="test_module1",
        )

    def test_serializer_contains_all_fields(self):
        """Ensure the serializer includes all expected fields."""
        serializer = CourseModuleSerializer(instance=self.course_module1)
        data = serializer.data
        self.assertEqual(data["title"], "test_module1")
        self.assertEqual(data["course"], self.course1.id)
        self.assertEqual(data["course_title"], self.course1.title)
        self.assertEqual(data["content_type"], "chat.chatroom")
        self.assertEqual(data["object_id"], self.chat_room1.id)
        self.assertEqual(data["order"], 0)

    def test_serializer_validation(self):
        """Test serializer validation logic."""
        payload = {
            "title": "test_module1",
            "course": self.course1.id,
            "content_type": "chat.chatroom",
            "object_id": self.chat_room1.id,
            "order": 0,
        }
        serializer = CourseModuleSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_content_type(self):
        """Test serializer with invalid content type."""
        payload = {
            "title": "test_module1",
            "course": self.course1.id,
            "content_type": "invalid.content.type",
            "object_id": self.chat_room1.id,
            "order": 0,
        }
        serializer = CourseModuleSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("content_type", serializer.errors)

    def test_serializer_invalid_object_id(self):
        """Test serializer with invalid object ID."""
        payload = {
            "title": "test_module1",
            "course": self.course1.id,
            "content_type": "chat.chatroom",
            "object_id": 99999,  # Invalid object ID
            "order": 0,
        }
        serializer = CourseModuleSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("object_id", serializer.errors)

    def test_serializer_with_empty_object_id(self):
        """Test serializer with missing object ID."""
        payload = {
            "title": "test_module1",
            "course": self.course1.id,
            "content_type": "chat.chatroom",
            "order": 0,
        }
        serializer = CourseModuleSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("object_id", serializer.errors)

    def test_serializer_to_representation(self):
        """Test the to_representation method for correct output."""
        serializer = CourseModuleSerializer(instance=self.course_module1)
        data = serializer.to_representation(self.course_module1)
        self.assertEqual(data["title"], "test_module1")
        self.assertEqual(data["course"], self.course1.id)
        self.assertEqual(data["course_title"], self.course1.title)
        self.assertEqual(data["content_type"], "chat.chatroom")
        self.assertEqual(data["object_id"], self.chat_room1.id)
        self.assertEqual(data["order"], 0)
