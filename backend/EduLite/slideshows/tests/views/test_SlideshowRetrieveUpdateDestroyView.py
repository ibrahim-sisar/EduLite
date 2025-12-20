"""Tests for SlideshowRetrieveUpdateDestroyView."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from slideshows.models import Slideshow, Slide

User = get_user_model()


class SlideshowRetrieveUpdateDestroyViewTestCase(TestCase):
    """Test cases for slideshow detail, update, and delete endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="password123"
        )
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="password123"
        )

        # Create course        # Create memberships        # Create slideshow with slides
        self.slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            visibility="public",
            created_by=self.teacher,
            is_published=True,
        )
        for i in range(10):
            Slide.objects.create(
                slideshow=self.slideshow,
                order=i,
                content=f"# Slide {i}\n\nContent here",
            )

        self.url = reverse(
            "slideshows:slideshow-detail", kwargs={"pk": self.slideshow.pk}
        )

    def test_detail_initial_param_limits_slides(self):
        """Test that ?initial=N limits slides returned."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"{self.url}?initial=3")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["slides"]), 3)
        self.assertEqual(response.data["slide_count"], 10)

    def test_detail_includes_remaining_slide_ids(self):
        """Test that remaining_slide_ids are included with ?initial."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"{self.url}?initial=3")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["remaining_slide_ids"]), 7)

    def test_detail_students_blocked_from_unpublished(self):
        """Test that students cannot access unpublished slideshows."""
        self.slideshow.is_published = False
        self.slideshow.save()

        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_teachers_see_unpublished(self):
        """Test that teachers can access unpublished slideshows."""
        self.slideshow.is_published = False
        self.slideshow.save()

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_increments_version(self):
        """Test that updating increments version number."""
        original_version = self.slideshow.version

        self.client.force_authenticate(user=self.teacher)
        data = {"title": "Updated Title"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["version"], original_version + 1)

    def test_update_requires_teacher_role(self):
        """Test that only teachers/assistants can update slideshows."""
        self.client.force_authenticate(user=self.student)
        data = {"title": "Student Update"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_teacher_role(self):
        """Test that only teachers/assistants can delete slideshows."""
        self.client.force_authenticate(user=self.student)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_success(self):
        """Test successful deletion by teacher."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Slideshow.objects.filter(pk=self.slideshow.pk).exists())

    def test_individual_slide_fetch(self):
        """Test fetching individual slide."""
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], slide.id)

    def test_update_individual_slide_requires_instructor_role(self):
        """Test that only instructors can update individual slides."""
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.student)
        data = {"content": "# Student Update"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_individual_slide_success(self):
        """Test successful update of individual slide."""
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# Updated Content\n\nNew information here"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Updated Content", response.data["content"])

        # Verify in database
        slide.refresh_from_db()
        self.assertIn("Updated Content", slide.content)

    def test_update_individual_slide_increments_slideshow_version(self):
        """Test that updating a slide increments the slideshow version."""
        original_version = self.slideshow.version
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# Version Test Update"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify version incremented
        self.slideshow.refresh_from_db()
        self.assertEqual(self.slideshow.version, original_version + 1)

    def test_update_individual_slide_re_renders_markdown(self):
        """Test that updating slide re-renders markdown."""
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# New Title\n\n**Bold** text"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check rendered content includes HTML
        self.assertIn("New Title", response.data["rendered_content"])
        self.assertIn("<strong>Bold</strong>", response.data["rendered_content"])

    def test_delete_individual_slide_requires_instructor_role(self):
        """Test that only instructors can delete individual slides."""
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.student)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_individual_slide_success(self):
        """Test successful deletion of individual slide."""
        slide = self.slideshow.slides.first()
        slide_id = slide.id
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        initial_count = self.slideshow.slides.count()

        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify slide deleted
        self.assertFalse(Slide.objects.filter(pk=slide_id).exists())
        # Verify slide count decreased
        self.assertEqual(self.slideshow.slides.count(), initial_count - 1)

    def test_delete_individual_slide_increments_slideshow_version(self):
        """Test that deleting a slide increments slideshow version."""
        original_version = self.slideshow.version
        slide = self.slideshow.slides.first()
        url = reverse(
            "slideshows:slide-detail",
            kwargs={"pk": self.slideshow.pk, "slide_id": slide.pk},
        )

        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify version incremented
        self.slideshow.refresh_from_db()
        self.assertEqual(self.slideshow.version, original_version + 1)
