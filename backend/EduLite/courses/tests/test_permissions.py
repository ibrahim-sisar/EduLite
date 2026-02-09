"""Tests for courses app custom permissions."""

from typing import Optional

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from courses.models import Course, CourseMembership
from courses.permissions import CanCreateCourse, IsCourseTeacher, IsCourseMember

User = get_user_model()


class CanCreateCoursePermissionTests(APITestCase):
    """Test the CanCreateCourse permission with setting toggle."""

    def setUp(self):
        self.url = reverse("course-create")

    def _create_user(self, username: str, occupation: Optional[str] = None):
        user = User.objects.create_user(username=username, password="test-pass-123")
        if occupation is not None:
            profile = user.profile
            profile.occupation = occupation
            profile.save()
        return user

    @override_settings(COURSE_CREATION_REQUIRES_TEACHER=True)
    def test_teacher_can_create_when_setting_true(self):
        teacher = self._create_user("teacher1", "teacher")
        self.client.force_authenticate(user=teacher)
        response = self.client.post(self.url, {"title": "Test Course"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(COURSE_CREATION_REQUIRES_TEACHER=True)
    def test_non_teacher_denied_when_setting_true(self):
        student = self._create_user("student1", "student")
        self.client.force_authenticate(user=student)
        response = self.client.post(self.url, {"title": "Test Course"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(COURSE_CREATION_REQUIRES_TEACHER=False)
    def test_any_user_can_create_when_setting_false(self):
        student = self._create_user("student2", "student")
        self.client.force_authenticate(user=student)
        response = self.client.post(self.url, {"title": "Test Course"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(COURSE_CREATION_REQUIRES_TEACHER=False)
    def test_unauthenticated_denied_even_when_setting_false(self):
        response = self.client.post(self.url, {"title": "Test Course"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(COURSE_CREATION_REQUIRES_TEACHER=True)
    def test_user_without_occupation_denied_when_setting_true(self):
        """User with no occupation set should be denied when teacher is required."""
        user = self._create_user("noocc")
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {"title": "Test Course"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IsCourseTeacherPermissionTests(TestCase):
    """Test the IsCourseTeacher permission class."""

    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user(
            username="teacher", password="test-pass-123"
        )
        cls.student = User.objects.create_user(
            username="student", password="test-pass-123"
        )
        cls.outsider = User.objects.create_user(
            username="outsider", password="test-pass-123"
        )
        cls.course = Course.objects.create(title="Test Course")
        CourseMembership.objects.create(
            user=cls.teacher, course=cls.course, role="teacher", status="enrolled"
        )
        CourseMembership.objects.create(
            user=cls.student, course=cls.course, role="student", status="enrolled"
        )

    def _make_request(self, user):
        factory = APIRequestFactory()
        request = factory.get("/fake/")
        request.user = user
        return request

    def _make_view(self, pk=None):
        class FakeView:
            kwargs = {}

        view = FakeView()
        if pk is not None:
            view.kwargs["pk"] = pk
        return view

    def test_teacher_has_permission(self):
        perm = IsCourseTeacher()
        request = self._make_request(self.teacher)
        view = self._make_view(pk=self.course.pk)
        self.assertTrue(perm.has_permission(request, view))

    def test_student_denied_permission(self):
        perm = IsCourseTeacher()
        request = self._make_request(self.student)
        view = self._make_view(pk=self.course.pk)
        self.assertFalse(perm.has_permission(request, view))

    def test_outsider_denied_permission(self):
        perm = IsCourseTeacher()
        request = self._make_request(self.outsider)
        view = self._make_view(pk=self.course.pk)
        self.assertFalse(perm.has_permission(request, view))

    def test_teacher_has_object_permission(self):
        perm = IsCourseTeacher()
        request = self._make_request(self.teacher)
        view = self._make_view()
        self.assertTrue(perm.has_object_permission(request, view, self.course))

    def test_student_denied_object_permission(self):
        perm = IsCourseTeacher()
        request = self._make_request(self.student)
        view = self._make_view()
        self.assertFalse(perm.has_object_permission(request, view, self.course))


class IsCourseMemberPermissionTests(TestCase):
    """Test the IsCourseMember permission class."""

    @classmethod
    def setUpTestData(cls):
        cls.member = User.objects.create_user(
            username="member", password="test-pass-123"
        )
        cls.pending = User.objects.create_user(
            username="pending", password="test-pass-123"
        )
        cls.outsider = User.objects.create_user(
            username="outsider", password="test-pass-123"
        )
        cls.course = Course.objects.create(title="Test Course")
        CourseMembership.objects.create(
            user=cls.member, course=cls.course, role="student", status="enrolled"
        )
        CourseMembership.objects.create(
            user=cls.pending, course=cls.course, role="student", status="pending"
        )

    def _make_request(self, user):
        factory = APIRequestFactory()
        request = factory.get("/fake/")
        request.user = user
        return request

    def _make_view(self, pk=None):
        class FakeView:
            kwargs = {}

        view = FakeView()
        if pk is not None:
            view.kwargs["pk"] = pk
        return view

    def test_enrolled_member_has_permission(self):
        perm = IsCourseMember()
        request = self._make_request(self.member)
        view = self._make_view(pk=self.course.pk)
        self.assertTrue(perm.has_permission(request, view))

    def test_pending_member_denied_permission(self):
        perm = IsCourseMember()
        request = self._make_request(self.pending)
        view = self._make_view(pk=self.course.pk)
        self.assertFalse(perm.has_permission(request, view))

    def test_outsider_denied_permission(self):
        perm = IsCourseMember()
        request = self._make_request(self.outsider)
        view = self._make_view(pk=self.course.pk)
        self.assertFalse(perm.has_permission(request, view))

    def test_enrolled_member_has_object_permission(self):
        perm = IsCourseMember()
        request = self._make_request(self.member)
        view = self._make_view()
        self.assertTrue(perm.has_object_permission(request, view, self.course))

    def test_pending_member_denied_object_permission(self):
        perm = IsCourseMember()
        request = self._make_request(self.pending)
        view = self._make_view()
        self.assertFalse(perm.has_object_permission(request, view, self.course))
