"""Tests for the course membership management API endpoints."""

from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership


class CourseMembershipManageAPITests(APITestCase):
    """Validate course membership list/invite/approve/deny/role/remove behaviour."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        # Users
        cls.teacher = cls._make_user("teacher_user", "teacher")
        cls.teacher2 = cls._make_user("teacher2_user", "teacher")
        cls.student = cls._make_user("student_user", "student")
        cls.outsider = cls._make_user("outsider_user", "student")
        cls.invite_target = cls._make_user("invite_target", "student")

        # Course
        cls.course = Course.objects.create(
            title="Test Course",
            outline="A course for testing membership management.",
            language="en",
            country="US",
            subject="physics",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )

        # Memberships
        cls.teacher_membership = CourseMembership.objects.create(
            course=cls.course, user=cls.teacher, role="teacher", status="enrolled"
        )
        cls.teacher2_membership = CourseMembership.objects.create(
            course=cls.course, user=cls.teacher2, role="teacher", status="enrolled"
        )
        cls.student_membership = CourseMembership.objects.create(
            course=cls.course, user=cls.student, role="student", status="enrolled"
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
        return reverse("course-membership-list-invite", kwargs={"pk": self.course.pk})

    def _detail_url(self, membership_id):
        return reverse(
            "course-membership-detail",
            kwargs={"pk": self.course.pk, "membership_id": membership_id},
        )

    # --- List (GET) ---

    def test_list_members_as_member(self):
        """Enrolled members can list course members with pagination."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self._list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Paginated response has 'results' key
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 3)

    def test_list_members_as_non_member(self):
        """Non-members are denied access."""
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(self._list_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_members_unauthenticated(self):
        """Unauthenticated clients are rejected."""
        response = self.client.get(self._list_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Invite (POST) ---

    def test_invite_user_as_teacher(self):
        """Teachers can invite users to the course."""
        self.client.force_authenticate(user=self.teacher)
        payload = {"user": self.invite_target.pk, "role": "student"}

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "invited")
        self.assertEqual(response.data["role"], "student")
        self.assertEqual(response.data["user"], self.invite_target.pk)

        # Cleanup for other tests using setUpTestData
        CourseMembership.objects.filter(
            course=self.course, user=self.invite_target
        ).delete()

    def test_invite_already_member(self):
        """Inviting an existing member returns 409 Conflict."""
        self.client.force_authenticate(user=self.teacher)
        payload = {"user": self.student.pk}

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_invite_as_student(self):
        """Students cannot invite users."""
        self.client.force_authenticate(user=self.student)
        payload = {"user": self.invite_target.pk}

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_invalid_role(self):
        """Inviting with an invalid role returns 400."""
        self.client.force_authenticate(user=self.teacher)
        payload = {"user": self.invite_target.pk, "role": "admin"}

        response = self.client.post(self._list_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.data)

    # --- Approve (PATCH) ---

    def test_approve_pending_member(self):
        """Teachers can approve a pending member."""
        self.client.force_authenticate(user=self.teacher)

        pending = CourseMembership.objects.create(
            course=self.course,
            user=self.invite_target,
            role="student",
            status="pending",
        )

        response = self.client.patch(
            self._detail_url(pending.pk),
            {"status": "enrolled"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "enrolled")

        # Cleanup
        pending.delete()

    # --- Deny (PATCH status="denied") ---

    def test_deny_pending_member(self):
        """Denying a member deletes the membership and returns 204."""
        self.client.force_authenticate(user=self.teacher)

        pending = CourseMembership.objects.create(
            course=self.course,
            user=self.invite_target,
            role="student",
            status="pending",
        )

        response = self.client.patch(
            self._detail_url(pending.pk),
            {"status": "denied"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMembership.objects.filter(pk=pending.pk).exists())

    # --- Role change (PATCH) ---

    def test_change_role_as_teacher(self):
        """Teachers can change a member's role."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            self._detail_url(self.student_membership.pk),
            {"role": "assistant"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "assistant")

        # Restore original role
        self.student_membership.refresh_from_db()
        self.student_membership.role = "student"
        self.student_membership.save()

    def test_cannot_demote_last_teacher(self):
        """Cannot demote a teacher if they are the last one."""
        # Create an isolated course with a single teacher
        solo_course = Course.objects.create(
            title="Solo Course",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        solo_membership = CourseMembership.objects.create(
            course=solo_course, user=self.teacher, role="teacher", status="enrolled"
        )
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            reverse(
                "course-membership-detail",
                kwargs={"pk": solo_course.pk, "membership_id": solo_membership.pk},
            ),
            {"role": "student"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # --- Non-teacher cannot manage ---

    def test_student_cannot_patch_membership(self):
        """Students cannot update memberships."""
        self.client.force_authenticate(user=self.student)

        response = self.client.patch(
            self._detail_url(self.student_membership.pk),
            {"role": "teacher"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_delete_membership(self):
        """Students cannot remove members."""
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self._detail_url(self.student_membership.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Remove (DELETE) ---

    def test_remove_member_as_teacher(self):
        """Teachers can remove a member."""
        self.client.force_authenticate(user=self.teacher)

        removable = CourseMembership.objects.create(
            course=self.course,
            user=self.invite_target,
            role="student",
            status="enrolled",
        )

        response = self.client.delete(self._detail_url(removable.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMembership.objects.filter(pk=removable.pk).exists())

    def test_cannot_remove_last_teacher(self):
        """Cannot remove the last teacher from a course."""
        # Create an isolated course with a single teacher
        solo_course = Course.objects.create(
            title="Solo Course 2",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        solo_membership = CourseMembership.objects.create(
            course=solo_course, user=self.teacher, role="teacher", status="enrolled"
        )
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(
            reverse(
                "course-membership-detail",
                kwargs={"pk": solo_course.pk, "membership_id": solo_membership.pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(CourseMembership.objects.filter(pk=solo_membership.pk).exists())
