from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory

from chat.models import ChatRoom
from ...models import Course, CourseMembership, CourseModule
from ...serializers import CourseDetailSerializer

User = get_user_model()


class CourseDetailSerializerTest(TestCase):
    """Test suite for CourseDetailSerializer."""

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.teacher = User.objects.create_user(
            username="teacher1", password="pass12345", email="teacher1@example.com"
        )
        cls.student = User.objects.create_user(
            username="student1", password="pass12345", email="student1@example.com"
        )
        cls.outsider = User.objects.create_user(
            username="outsider", password="pass12345", email="outsider@example.com"
        )
        cls.course = Course.objects.create(
            title="Detail Test Course",
            outline="A course for detail testing",
            language="en",
            country="US",
            subject="physics",
            visibility="public",
            start_date=datetime(2025, 9, 1, 8, 0, 0),
            end_date=datetime(2025, 12, 15, 20, 0, 0),
            is_active=True,
            allow_join_requests=True,
        )
        cls.teacher_membership = CourseMembership.objects.create(
            user=cls.teacher, course=cls.course, role="teacher", status="enrolled"
        )
        cls.student_membership = CourseMembership.objects.create(
            user=cls.student, course=cls.course, role="student", status="enrolled"
        )
        # Create a module using ChatRoom as the content object
        cls.chatroom = ChatRoom.objects.create(name="Test Room", creator=cls.teacher)
        cls.module = CourseModule.objects.create(
            course=cls.course,
            title="Chat Module",
            order=0,
            content_type=ContentType.objects.get_for_model(ChatRoom),
            object_id=cls.chatroom.pk,
        )

    def _get_context(self, user=None):
        """Helper to build serializer context with a request."""
        request = self.factory.get("/")
        if user:
            request.user = user
        else:
            from django.contrib.auth.models import AnonymousUser

            request.user = AnonymousUser()
        return {"request": request}

    def test_detail_serializer_contains_expected_fields(self):
        """Test that detail serializer includes all expected fields."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.teacher)
        )
        expected_fields = {
            "id",
            "title",
            "outline",
            "language",
            "country",
            "subject",
            "visibility",
            "start_date",
            "end_date",
            "duration_time",
            "allow_join_requests",
            "is_active",
            "member_count",
            "user_role",
            "members",
            "modules",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_detail_serializer_nested_members(self):
        """Test that members are nested in the output."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.teacher)
        )
        members = serializer.data["members"]
        self.assertEqual(len(members), 2)
        usernames = {m["user_name"] for m in members}
        self.assertEqual(usernames, {"teacher1", "student1"})

    def test_detail_serializer_nested_modules(self):
        """Test that modules are nested in the output."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.teacher)
        )
        modules = serializer.data["modules"]
        self.assertEqual(len(modules), 1)
        self.assertEqual(modules[0]["title"], "Chat Module")
        self.assertEqual(modules[0]["order"], 0)

    def test_detail_serializer_member_count(self):
        """Test that member_count matches actual memberships."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.teacher)
        )
        self.assertEqual(serializer.data["member_count"], 2)

    def test_detail_serializer_duration_time(self):
        """Test that duration_time is computed correctly."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.teacher)
        )
        # Sep 1 08:00 to Dec 15 20:00
        expected_minutes = (
            self.course.end_date - self.course.start_date
        ).total_seconds() // 60
        self.assertEqual(serializer.data["duration_time"], expected_minutes)

    def test_detail_serializer_user_role_teacher(self):
        """Test that user_role returns 'teacher' for a teacher member."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.teacher)
        )
        self.assertEqual(serializer.data["user_role"], "teacher")

    def test_detail_serializer_user_role_student(self):
        """Test that user_role returns 'student' for a student member."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.student)
        )
        self.assertEqual(serializer.data["user_role"], "student")

    def test_detail_serializer_user_role_null_for_non_member(self):
        """Test that user_role returns null for a user not in the course."""
        serializer = CourseDetailSerializer(
            self.course, context=self._get_context(self.outsider)
        )
        self.assertIsNone(serializer.data["user_role"])

    def test_detail_serializer_user_role_null_for_anonymous(self):
        """Test that user_role returns null for an anonymous user."""
        serializer = CourseDetailSerializer(self.course, context=self._get_context())
        self.assertIsNone(serializer.data["user_role"])
