"""Tests for the course enrollment (join/leave) API endpoints."""

from datetime import datetime
from typing import Optional

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, CourseMembership


class CourseEnrollAPITests(APITestCase):
    """Validate POST (join) and DELETE (leave) on /api/courses/<pk>/enroll/."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        cls.teacher = cls._make_user("teacher_user", "teacher")
        cls.student = cls._make_user("student_user", "student")
        cls.outsider = cls._make_user("outsider_user", "student")

        # Public course
        cls.public_course = Course.objects.create(
            title="Public Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.public_course,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
        )

        # Restricted course with join requests
        cls.restricted_open = Course.objects.create(
            title="Restricted Open",
            visibility="restricted",
            allow_join_requests=True,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.restricted_open,
            user=cls.teacher,
            role="teacher",
            status="enrolled",
        )

        # Restricted course without join requests
        cls.restricted_closed = Course.objects.create(
            title="Restricted Closed",
            visibility="restricted",
            allow_join_requests=False,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )

        # Private course
        cls.private_course = Course.objects.create(
            title="Private Course",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
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

    def _enroll_url(self, course):
        return reverse("course-enroll", kwargs={"pk": course.pk})

    # --- Join (POST) ---

    def test_join_public_course(self):
        """Joining a public course creates an enrolled membership."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "enrolled")
        self.assertEqual(response.data["role"], "student")

        # Cleanup
        CourseMembership.objects.filter(
            course=self.public_course, user=self.outsider
        ).delete()

    def test_join_restricted_with_join_requests(self):
        """Joining a restricted course with allow_join_requests creates a pending membership."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.restricted_open))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["role"], "student")

        # Cleanup
        CourseMembership.objects.filter(
            course=self.restricted_open, user=self.outsider
        ).delete()

    def test_join_restricted_without_join_requests(self):
        """Joining a restricted course without allow_join_requests is denied."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.restricted_closed))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_private_course(self):
        """Joining a private course is denied."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.post(self._enroll_url(self.private_course))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_join_already_member(self):
        """Joining a course you're already in returns 409."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_join_unauthenticated(self):
        """Unauthenticated users cannot join courses."""
        response = self.client.post(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Leave (DELETE) ---

    def test_leave_course(self):
        """A member can leave a course."""
        # Create a membership to leave
        membership = CourseMembership.objects.create(
            course=self.public_course,
            user=self.student,
            role="student",
            status="enrolled",
        )
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMembership.objects.filter(pk=membership.pk).exists())

    def test_last_teacher_cannot_leave(self):
        """The last teacher in a course cannot leave."""
        # Create a solo-teacher course
        solo_course = Course.objects.create(
            title="Solo Teacher Course",
            visibility="public",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=solo_course,
            user=self.teacher,
            role="teacher",
            status="enrolled",
        )
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(self._enroll_url(solo_course))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_non_member_leave(self):
        """Leaving a course you're not in returns 404."""
        self.client.force_authenticate(user=self.outsider)

        response = self.client.delete(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_leave_unauthenticated(self):
        """Unauthenticated users cannot leave courses."""
        response = self.client.delete(self._enroll_url(self.public_course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CourseInvitationAcceptDeclineAPITests(APITestCase):
    """Validate POST on /api/courses/<pk>/enroll/accept/ and /enroll/decline/."""

    @classmethod
    def setUpTestData(cls):
        cls.user_model = get_user_model()

        cls.teacher = cls._make_user("inv_teacher", "teacher")
        cls.invited_user = cls._make_user("inv_student", "student")
        cls.other_user = cls._make_user("inv_other", "student")

        cls.course = Course.objects.create(
            title="Invitation Test Course",
            visibility="private",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
        )
        CourseMembership.objects.create(
            course=cls.course,
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

    def _accept_url(self, course):
        return reverse("course-enroll-accept", kwargs={"pk": course.pk})

    def _decline_url(self, course):
        return reverse("course-enroll-decline", kwargs={"pk": course.pk})

    def _create_invitation(self, user, course=None):
        """Helper to create an invitation membership."""
        return CourseMembership.objects.create(
            course=course or self.course,
            user=user,
            role="student",
            status="invited",
        )

    # --- Accept Invitation ---

    def test_accept_invitation(self):
        """User with status='invited' can accept, status becomes 'enrolled'."""
        invitation = self._create_invitation(self.invited_user)
        self.client.force_authenticate(user=self.invited_user)

        response = self.client.post(self._accept_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "enrolled")
        self.assertEqual(response.data["role"], "student")

        invitation.refresh_from_db()
        self.assertEqual(invitation.status, "enrolled")

        # Cleanup
        invitation.delete()

    def test_accept_without_invitation(self):
        """User with no invitation gets 404."""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self._accept_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_already_enrolled(self):
        """User with status='enrolled' gets 404 (no invitation to accept)."""
        membership = CourseMembership.objects.create(
            course=self.course,
            user=self.invited_user,
            role="student",
            status="enrolled",
        )
        self.client.force_authenticate(user=self.invited_user)

        response = self.client.post(self._accept_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Cleanup
        membership.delete()

    def test_accept_pending_gets_404(self):
        """User with status='pending' gets 404 (not an invitation)."""
        membership = CourseMembership.objects.create(
            course=self.course,
            user=self.invited_user,
            role="student",
            status="pending",
        )
        self.client.force_authenticate(user=self.invited_user)

        response = self.client.post(self._accept_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Cleanup
        membership.delete()

    def test_accept_unauthenticated(self):
        """Unauthenticated request returns 401."""
        response = self.client.post(self._accept_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Decline Invitation ---

    def test_decline_invitation(self):
        """User with status='invited' can decline, membership is deleted."""
        invitation = self._create_invitation(self.invited_user)
        invitation_pk = invitation.pk
        self.client.force_authenticate(user=self.invited_user)

        response = self.client.post(self._decline_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CourseMembership.objects.filter(pk=invitation_pk).exists())

    def test_decline_without_invitation(self):
        """User with no invitation gets 404."""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self._decline_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_already_enrolled(self):
        """User with status='enrolled' gets 404 (no invitation to decline)."""
        membership = CourseMembership.objects.create(
            course=self.course,
            user=self.invited_user,
            role="student",
            status="enrolled",
        )
        self.client.force_authenticate(user=self.invited_user)

        response = self.client.post(self._decline_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Cleanup
        membership.delete()

    def test_decline_unauthenticated(self):
        """Unauthenticated request returns 401."""
        response = self.client.post(self._decline_url(self.course))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Cross-user safety ---

    def test_cannot_accept_other_users_invitation(self):
        """User A cannot accept user B's invitation — endpoint only operates on request.user."""
        self._create_invitation(self.invited_user)
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self._accept_url(self.course))

        # other_user has no invitation, so 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # invited_user's invitation is unchanged
        self.assertTrue(
            CourseMembership.objects.filter(
                course=self.course, user=self.invited_user, status="invited"
            ).exists()
        )

        # Cleanup
        CourseMembership.objects.filter(
            course=self.course, user=self.invited_user
        ).delete()
