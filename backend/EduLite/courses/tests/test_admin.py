# courses/tests/test_admin.py
# Tests for CourseAdmin teacher requirement enforcement

from datetime import datetime

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from ..admin import CourseAdmin
from ..models import Course, CourseMembership

User = get_user_model()


class _MockForm:
    """Mock form for testing save_related. Needs save_m2m for Django admin."""

    def __init__(self, instance):
        self.instance = instance

    def save_m2m(self):
        pass


class TestCourseAdminTeacherRequirement(TestCase):
    """Tests that CourseAdmin enforces at least one enrolled teacher."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = CourseAdmin(Course, self.site)
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.teacher_user = User.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="pass123",
        )
        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="pass123",
        )

    def test_save_related_raises_when_no_teacher(self):
        """Creating a course without a teacher membership should raise ValidationError."""
        course = Course.objects.create(
            title="No Teacher Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
        )

        request = self.factory.post("/admin/courses/course/add/")
        request.user = self.superuser

        with self.assertRaises(ValidationError) as ctx:
            self.admin.save_related(
                request, _MockForm(course), formsets=[], change=False
            )

        self.assertIn("at least one enrolled teacher", str(ctx.exception))

    def test_save_related_succeeds_with_teacher(self):
        """Creating a course with a teacher membership should succeed."""
        course = Course.objects.create(
            title="Has Teacher Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
        )
        CourseMembership.objects.create(
            user=self.teacher_user,
            course=course,
            role="teacher",
            status="enrolled",
        )

        request = self.factory.post("/admin/courses/course/add/")
        request.user = self.superuser

        # Should not raise
        self.admin.save_related(request, _MockForm(course), formsets=[], change=False)

    def test_save_related_raises_when_only_students(self):
        """A course with only student memberships should raise ValidationError."""
        course = Course.objects.create(
            title="Students Only Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
        )
        CourseMembership.objects.create(
            user=self.student_user,
            course=course,
            role="student",
            status="enrolled",
        )

        request = self.factory.post("/admin/courses/course/add/")
        request.user = self.superuser

        with self.assertRaises(ValidationError):
            self.admin.save_related(
                request, _MockForm(course), formsets=[], change=False
            )

    def test_save_related_raises_when_teacher_not_enrolled(self):
        """A teacher with 'invited' status should not count as an enrolled teacher."""
        course = Course.objects.create(
            title="Invited Teacher Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
        )
        CourseMembership.objects.create(
            user=self.teacher_user,
            course=course,
            role="teacher",
            status="invited",
        )

        request = self.factory.post("/admin/courses/course/add/")
        request.user = self.superuser

        with self.assertRaises(ValidationError):
            self.admin.save_related(
                request, _MockForm(course), formsets=[], change=False
            )

    def test_save_related_blocks_removing_last_teacher(self):
        """Removing the last teacher from an existing course should raise ValidationError."""
        course = Course.objects.create(
            title="Existing Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
        )
        membership = CourseMembership.objects.create(
            user=self.teacher_user,
            course=course,
            role="teacher",
            status="enrolled",
        )
        # Simulate removing the teacher (delete the membership before save_related check)
        membership.delete()

        request = self.factory.post(f"/admin/courses/course/{course.pk}/change/")
        request.user = self.superuser

        with self.assertRaises(ValidationError):
            self.admin.save_related(
                request, _MockForm(course), formsets=[], change=True
            )
