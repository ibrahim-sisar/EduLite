# courses/tests/test_Course.py
# Tests for the CourseModule model

from django.test import TestCase
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError

from ..models import Course, CourseModule
from chat.models import ChatRoom, Message

User = get_user_model()


class CourseModuleTest(TestCase):
    """
    Test the CourseModule model, which links a Course to any type of content
    using Django's GenericForeignKey (e.g., ChatRoom, Message).
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Set up test data for CourseModule:
        - a Course
        - two ChatRoom instances
        - a Message instance (to test GenericForeignKey cross-model binding)
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
        cls.chat_room2 = ChatRoom.objects.create(
            name="test_chat_room2",
            room_type="ONE_TO_ONE",
        )

        cls.user1 = User.objects.create_user(
            username="testuser1",
            password="password123",
            email="testuser1@example.com",
        )

        cls.message1 = Message.objects.create(
            chat_room=cls.chat_room1,
            sender=cls.user1,
            content="test_message1",
        )

    def test_course_module_creation(self) -> None:
        """Test that a CourseModule can be created with a ChatRoom as content."""
        chatroom_ct = ContentType.objects.get_for_model(ChatRoom)

        course_module = CourseModule.objects.create(
            course=self.course1,
            content_type=chatroom_ct,
            object_id=self.chat_room1.id,
        )
        course_module.full_clean()

        self.assertEqual(course_module.course, self.course1)
        self.assertEqual(course_module.content_object, self.chat_room1)

    def test_course_module_update_content_object_with_same_class(self) -> None:
        """Test updating the content_object to another ChatRoom instance."""
        chatroom_ct = ContentType.objects.get_for_model(ChatRoom)

        course_module = CourseModule.objects.create(
            course=self.course1,
            content_type=chatroom_ct,
            object_id=self.chat_room1.id,
        )
        course_module.full_clean()
        self.assertEqual(course_module.content_object, self.chat_room1)

        course_module.object_id = self.chat_room2.id
        course_module.save()
        course_module.refresh_from_db()

        self.assertEqual(course_module.content_object, self.chat_room2)

    def test_course_module_update_content_object_with_different_class(self) -> None:
        """Test updating the content_object to a different model (Message)."""
        chatroom_ct = ContentType.objects.get_for_model(ChatRoom)
        message_ct = ContentType.objects.get_for_model(Message)

        course_module = CourseModule.objects.create(
            course=self.course1,
            content_type=chatroom_ct,
            object_id=self.chat_room1.id,
        )
        course_module.full_clean()
        self.assertEqual(course_module.content_object, self.chat_room1)

        # Change to different model type (Message)
        course_module.content_type = message_ct
        course_module.object_id = self.message1.id
        course_module.save()
        course_module.refresh_from_db()

        self.assertEqual(course_module.content_object, self.message1)

    def test_course_module_str(self) -> None:
        """Test the string representation of CourseModule."""
        chatroom_ct = ContentType.objects.get_for_model(ChatRoom)

        course_module = CourseModule.objects.create(
            course=self.course1,
            content_type=chatroom_ct,
            object_id=self.chat_room1.id,
        )
        course_module.full_clean()

        expected_str = f"{self.course1.title} - module {course_module.order}"
        self.assertEqual(str(course_module), expected_str)

    def test_course_module_order(self) -> None:
        """Test the default and manual ordering of CourseModules."""
        chatroom_ct = ContentType.objects.get_for_model(ChatRoom)

        module1 = CourseModule.objects.create(
            course=self.course1,
            order=1,
            content_type=chatroom_ct,
            object_id=self.chat_room1.id,
        )
        module1.full_clean()
        self.assertEqual(module1.order, 1)

        module2 = CourseModule.objects.create(
            course=self.course1,
            content_type=chatroom_ct,
            object_id=self.chat_room2.id,
        )
        module2.full_clean()
        self.assertEqual(module2.order, 0)  # default

    def test_course_module_missing_content_type_or_object_id(self) -> None:
        """Test ValidationError raised when content_type or object_id is missing."""
        # missing content_type
        module = CourseModule(course=self.course1, object_id=self.chat_room1.id)
        with self.assertRaises(ValidationError):
            module.full_clean()

        # missing object_id
        ct = ContentType.objects.get_for_model(ChatRoom)
        module = CourseModule(course=self.course1, content_type=ct)
        with self.assertRaises(ValidationError):
            module.full_clean()

    def test_course_module_invalid_object_id(self) -> None:
        """Test ValidationError when object_id refers to a nonexistent instance."""
        ct = ContentType.objects.get_for_model(ChatRoom)
        invalid_id = 99999  # assumed to not exist

        module = CourseModule(
            course=self.course1, content_type=ct, object_id=invalid_id
        )
        with self.assertRaises(ValidationError):
            module.full_clean()

    def test_course_module_str_with_title(self):
        """Test string representation includes title if provided."""
        ct = ContentType.objects.get_for_model(ChatRoom)

        module = CourseModule.objects.create(
            course=self.course1,
            title="Lecture 1",
            content_type=ct,
            object_id=self.chat_room1.id,
        )
        self.assertEqual(str(module), f"{self.course1.title} - Lecture 1")
