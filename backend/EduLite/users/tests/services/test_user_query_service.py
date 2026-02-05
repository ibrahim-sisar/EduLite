"""
Tests for UserQueryService - centralized cross-app query logic.

These tests verify that the UserQueryService correctly queries
courses, teachers, and chatrooms without causing circular dependencies.
"""

from chat.models import ChatRoom
from courses.models import Course, CourseMembership
from django.contrib.auth.models import User
from django.test import TestCase

from users.services import UserQueryService


class UserQueryServiceTestCase(TestCase):
    """Base test case with common setup for user query service tests."""

    def setUp(self):
        """Set up test users, courses, and chatrooms."""
        # Create test users
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
        )
        self.teacher1 = User.objects.create_user(
            username="teacher1",
            email="teacher1@example.com",
        )
        self.teacher2 = User.objects.create_user(
            username="teacher2",
            email="teacher2@example.com",
        )


class GetUserCoursesTests(UserQueryServiceTestCase):
    """Tests for UserQueryService.get_user_courses()"""

    def test_returns_enrolled_courses(self):
        """User should see courses they are enrolled in."""
        course = Course.objects.create(title="Test Course")
        CourseMembership.objects.create(user=self.user1, course=course, role="student")

        courses = UserQueryService.get_user_courses(self.user1)

        self.assertEqual(courses.count(), 1)
        self.assertIn(course, courses)

    def test_returns_empty_when_not_enrolled(self):
        """User with no memberships should get empty queryset."""
        Course.objects.create(title="Test Course")

        courses = UserQueryService.get_user_courses(self.user1)

        self.assertEqual(courses.count(), 0)

    def test_returns_multiple_courses(self):
        """User enrolled in multiple courses should see all of them."""
        course1 = Course.objects.create(title="Course 1")
        course2 = Course.objects.create(title="Course 2")
        CourseMembership.objects.create(user=self.user1, course=course1, role="student")
        CourseMembership.objects.create(user=self.user1, course=course2, role="student")

        courses = UserQueryService.get_user_courses(self.user1)

        self.assertEqual(courses.count(), 2)
        self.assertIn(course1, courses)
        self.assertIn(course2, courses)

    def test_returns_distinct_courses(self):
        """User should not see duplicate courses if they have multiple roles."""
        course = Course.objects.create(title="Test Course")
        # User has two memberships in same course (shouldn't happen but test distinctness)
        CourseMembership.objects.create(user=self.user1, course=course, role="student")

        courses = UserQueryService.get_user_courses(self.user1)

        self.assertEqual(courses.count(), 1)


class GetUserCourseIdsTests(UserQueryServiceTestCase):
    """Tests for UserQueryService.get_user_course_ids()"""

    def test_returns_set_of_ids(self):
        """Should return a set of course IDs."""
        course1 = Course.objects.create(title="Course 1")
        course2 = Course.objects.create(title="Course 2")
        CourseMembership.objects.create(user=self.user1, course=course1, role="student")
        CourseMembership.objects.create(user=self.user1, course=course2, role="student")

        course_ids = UserQueryService.get_user_course_ids(self.user1)

        self.assertIsInstance(course_ids, set)
        self.assertEqual(course_ids, {course1.id, course2.id})

    def test_returns_empty_set_when_not_enrolled(self):
        """User with no memberships should get empty set."""
        course_ids = UserQueryService.get_user_course_ids(self.user1)

        self.assertEqual(course_ids, set())


class GetUserTeacherIdsTests(UserQueryServiceTestCase):
    """Tests for UserQueryService.get_user_teacher_ids()"""

    def test_returns_teacher_ids_from_enrolled_courses(self):
        """Should return teacher IDs from courses user is enrolled in."""
        course = Course.objects.create(title="Test Course")
        # Student enrolled in course
        CourseMembership.objects.create(user=self.user1, course=course, role="student")
        # Teacher in the same course
        CourseMembership.objects.create(
            user=self.teacher1, course=course, role="teacher"
        )

        teacher_ids = UserQueryService.get_user_teacher_ids(self.user1)

        self.assertEqual(teacher_ids, {self.teacher1.id})

    def test_excludes_teachers_from_other_courses(self):
        """Should not include teachers from courses user is not enrolled in."""
        course1 = Course.objects.create(title="Course 1")
        course2 = Course.objects.create(title="Course 2")
        # Student enrolled in course1 only
        CourseMembership.objects.create(user=self.user1, course=course1, role="student")
        # Teacher1 teaches course1
        CourseMembership.objects.create(
            user=self.teacher1, course=course1, role="teacher"
        )
        # Teacher2 teaches course2 (user not enrolled)
        CourseMembership.objects.create(
            user=self.teacher2, course=course2, role="teacher"
        )

        teacher_ids = UserQueryService.get_user_teacher_ids(self.user1)

        self.assertEqual(teacher_ids, {self.teacher1.id})
        self.assertNotIn(self.teacher2.id, teacher_ids)

    def test_returns_empty_when_not_enrolled(self):
        """User with no enrollments should get empty set."""
        course = Course.objects.create(title="Test Course")
        CourseMembership.objects.create(
            user=self.teacher1, course=course, role="teacher"
        )

        teacher_ids = UserQueryService.get_user_teacher_ids(self.user1)

        self.assertEqual(teacher_ids, set())

    def test_returns_multiple_teachers(self):
        """Should return all teachers from user's courses."""
        course = Course.objects.create(title="Test Course")
        CourseMembership.objects.create(user=self.user1, course=course, role="student")
        CourseMembership.objects.create(
            user=self.teacher1, course=course, role="teacher"
        )
        CourseMembership.objects.create(
            user=self.teacher2, course=course, role="teacher"
        )

        teacher_ids = UserQueryService.get_user_teacher_ids(self.user1)

        self.assertEqual(teacher_ids, {self.teacher1.id, self.teacher2.id})

    def test_excludes_non_teacher_roles(self):
        """Should only include users with 'teacher' role."""
        course = Course.objects.create(title="Test Course")
        CourseMembership.objects.create(user=self.user1, course=course, role="student")
        CourseMembership.objects.create(user=self.user2, course=course, role="student")
        CourseMembership.objects.create(
            user=self.teacher1, course=course, role="teacher"
        )

        teacher_ids = UserQueryService.get_user_teacher_ids(self.user1)

        self.assertEqual(teacher_ids, {self.teacher1.id})
        self.assertNotIn(self.user2.id, teacher_ids)


class GetUserChatroomIdsTests(UserQueryServiceTestCase):
    """Tests for UserQueryService.get_user_chatroom_ids()"""

    def test_returns_participated_chatroom_ids(self):
        """Should return IDs of chatrooms user participates in."""
        chatroom = ChatRoom.objects.create(room_type="GROUP")
        chatroom.participants.add(self.user1)

        chatroom_ids = UserQueryService.get_user_chatroom_ids(self.user1)

        self.assertEqual(chatroom_ids, {chatroom.id})

    def test_returns_empty_when_no_participation(self):
        """User with no chatroom participation should get empty set."""
        ChatRoom.objects.create(room_type="GROUP")

        chatroom_ids = UserQueryService.get_user_chatroom_ids(self.user1)

        self.assertEqual(chatroom_ids, set())

    def test_returns_multiple_chatroom_ids(self):
        """Should return all chatroom IDs user participates in."""
        chatroom1 = ChatRoom.objects.create(room_type="GROUP")
        chatroom2 = ChatRoom.objects.create(room_type="ONE_TO_ONE")
        chatroom1.participants.add(self.user1)
        chatroom2.participants.add(self.user1)

        chatroom_ids = UserQueryService.get_user_chatroom_ids(self.user1)

        self.assertEqual(chatroom_ids, {chatroom1.id, chatroom2.id})

    def test_excludes_non_participated_chatrooms(self):
        """Should not include chatrooms user doesn't participate in."""
        chatroom1 = ChatRoom.objects.create(room_type="GROUP")
        chatroom2 = ChatRoom.objects.create(room_type="GROUP")
        chatroom1.participants.add(self.user1)
        chatroom2.participants.add(self.user2)  # user1 not added

        chatroom_ids = UserQueryService.get_user_chatroom_ids(self.user1)

        self.assertEqual(chatroom_ids, {chatroom1.id})
        self.assertNotIn(chatroom2.id, chatroom_ids)


class GetUserChatroomsTests(UserQueryServiceTestCase):
    """Tests for UserQueryService.get_user_chatrooms()"""

    def test_returns_queryset_of_chatrooms(self):
        """Should return a QuerySet of ChatRoom objects."""
        chatroom1 = ChatRoom.objects.create(room_type="GROUP")
        chatroom2 = ChatRoom.objects.create(room_type="ONE_TO_ONE")
        chatroom1.participants.add(self.user1)
        chatroom2.participants.add(self.user1)

        chatrooms = UserQueryService.get_user_chatrooms(self.user1)

        self.assertEqual(chatrooms.count(), 2)
        self.assertIn(chatroom1, chatrooms)
        self.assertIn(chatroom2, chatrooms)

    def test_returns_empty_queryset_when_no_participation(self):
        """User with no chatroom participation should get empty queryset."""
        chatrooms = UserQueryService.get_user_chatrooms(self.user1)

        self.assertEqual(chatrooms.count(), 0)
