"""Tests for SlideCreateView."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from slideshows.models import Slideshow, Slide

User = get_user_model()


class SlideCreateViewTestCase(TestCase):
    """Test cases for creating individual slides."""

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
        self.other_teacher = User.objects.create_user(
            username="other_teacher",
            email="other_teacher@test.com",
            password="password123",
        )

        # Create course        # Create memberships        # Create slideshow
        self.slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            visibility="public",
            created_by=self.teacher,
            is_published=True,
        )

        # Add initial slides
        for i in range(3):
            Slide.objects.create(
                slideshow=self.slideshow, order=i, content=f"# Slide {i}"
            )

        self.url = reverse("slideshows:slide-create", kwargs={"pk": self.slideshow.pk})

    def test_create_slide_requires_authentication(self):
        """Test that creating a slide requires authentication."""
        data = {"content": "# New Slide"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_slide_requires_instructor_role(self):
        """Test that only instructors can create slides."""
        self.client.force_authenticate(user=self.student)
        data = {"content": "# Student Slide"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_slide_sets_slideshow_automatically(self):
        """Test that slideshow is automatically set from URL."""
        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# New Slide", "order": 5}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify slide belongs to correct slideshow
        slide = Slide.objects.get(pk=response.data["id"])
        self.assertEqual(slide.slideshow.id, self.slideshow.id)

    def test_create_slide_auto_assigns_order(self):
        """Test that order is auto-assigned if not provided."""
        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# Auto-Order Slide"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should be assigned order 3 (after existing 0, 1, 2)
        self.assertEqual(response.data["order"], 3)

    def test_create_slide_explicit_order(self):
        """Test creating slide with explicit order."""
        self.client.force_authenticate(user=self.teacher)
        data = {"order": 10, "content": "# Explicit Order Slide"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["order"], 10)

    def test_create_slide_increments_slideshow_version(self):
        """Test that creating a slide increments slideshow version."""
        original_version = self.slideshow.version

        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# Version Test Slide"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Refresh slideshow from DB
        self.slideshow.refresh_from_db()
        self.assertEqual(self.slideshow.version, original_version + 1)

    def test_create_slide_renders_markdown(self):
        """Test that markdown is rendered when slide is created."""
        self.client.force_authenticate(user=self.teacher)
        data = {
            "content": "# Test Slide\n\nWith **bold** text",
            "title": "Test Title",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("rendered_content", response.data)
        self.assertIsNotNone(response.data["rendered_content"])
        # Check that HTML was rendered
        self.assertIn("Test Slide", response.data["rendered_content"])
        self.assertIn("<strong>bold</strong>", response.data["rendered_content"])

    def test_create_slide_non_enrolled_instructor_forbidden(self):
        """Test that instructors from other courses cannot create slides."""
        self.client.force_authenticate(user=self.other_teacher)
        data = {"content": "# Unauthorized Slide"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_slide_invalid_slideshow_returns_404(self):
        """Test that invalid slideshow ID returns 404."""
        self.client.force_authenticate(user=self.teacher)
        url = reverse("slideshows:slide-create", kwargs={"pk": 99999})
        data = {"content": "# Slide for nonexistent slideshow"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_slide_count_increments(self):
        """Test that slide count increases after creation."""
        initial_count = self.slideshow.slides.count()

        self.client.force_authenticate(user=self.teacher)
        data = {"content": "# New Slide"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.slideshow.slides.count(), initial_count + 1)
