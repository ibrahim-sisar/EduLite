"""Tests for SlideshowListCreateView."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from slideshows.models import Slideshow, Slide

User = get_user_model()


class SlideshowListCreateViewTestCase(TestCase):
    """Test cases for slideshow list and create endpoints."""

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
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="password123"
        )

        # Create slideshows
        self.published_slideshow = Slideshow.objects.create(
            title="Published Slideshow",
            visibility="public",
            created_by=self.teacher,
            is_published=True,
        )
        self.unpublished_slideshow = Slideshow.objects.create(
            title="Unpublished Slideshow",
            visibility="public",
            created_by=self.teacher,
            is_published=False,
        )
        self.private_slideshow = Slideshow.objects.create(
            title="Private Slideshow",
            visibility="private",
            created_by=self.teacher,
            is_published=True,
        )

        self.url = reverse("slideshows:slideshow-list-create")

    def test_list_requires_authentication(self):
        """Test that listing slideshows requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_see_public_published_and_own(self):
        """Test that users see public published slideshows and their own."""
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see only the public published slideshow
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Published Slideshow")

    def test_list_owners_see_all_their_slideshows(self):
        """Test that owners see all their own slideshows."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see all 3 slideshows (owner can see private and unpublished)
        self.assertEqual(len(response.data), 3)

    def test_list_filters_by_visibility(self):
        """Test filtering slideshows by visibility."""
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"{self.url}?visibility=public")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see public slideshows
        for slideshow in response.data:
            self.assertEqual(slideshow["visibility"], "public")

    def test_list_filters_by_subject(self):
        """Test filtering slideshows by subject."""
        Slideshow.objects.create(
            title="Math Slideshow",
            visibility="public",
            subject="math",
            created_by=self.teacher,
            is_published=True,
        )

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"{self.url}?subject=math")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["subject"], "math")

    def test_list_mine_only_filter(self):
        """Test filtering for only user's own slideshows."""
        # Create slideshow by other user
        Slideshow.objects.create(
            title="Other User Slideshow",
            visibility="public",
            created_by=self.other_user,
            is_published=True,
        )

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(f"{self.url}?mine=true")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see teacher's slideshows
        for slideshow in response.data:
            self.assertEqual(slideshow["created_by"], self.teacher.id)

    def test_list_non_owner_sees_only_public_published(self):
        """Test that non-owners only see public published slideshows."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see the public published slideshow
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Published Slideshow")

    def test_create_requires_authentication(self):
        """Test that creating slideshows requires authentication."""
        data = {
            "title": "New Slideshow",
            "visibility": "private",
            "is_published": False,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_success(self):
        """Test successful slideshow creation."""
        self.client.force_authenticate(user=self.student)
        data = {
            "title": "Student's Slideshow",
            "description": "A slideshow created by a student",
            "visibility": "public",
            "subject": "cs",
            "is_published": False,
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Student's Slideshow")
        self.assertEqual(response.data["created_by"], self.student.id)
        self.assertEqual(response.data["visibility"], "public")

    def test_create_sets_created_by_automatically(self):
        """Test that created_by is set automatically from authenticated user."""
        self.client.force_authenticate(user=self.teacher)
        data = {
            "title": "Teacher's Slideshow",
            "visibility": "private",
            "is_published": False,
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["created_by"], self.teacher.id)
        self.assertEqual(response.data["created_by_username"], "teacher")

    def test_create_renders_slides_via_spellbook(self):
        """Test that slides are rendered when created."""
        self.client.force_authenticate(user=self.teacher)
        data = {
            "title": "Slideshow with Slides",
            "visibility": "public",
            "is_published": False,
            "slides": [
                {"order": 0, "content": "# First Slide\n\nContent here"},
                {"order": 1, "content": "# Second Slide"},
            ],
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["slides"]), 2)
        # Check that rendered_content exists
        self.assertIn("rendered_content", response.data["slides"][0])
        self.assertIsNotNone(response.data["slides"][0]["rendered_content"])

    def test_create_minimal_slideshow(self):
        """Test creating slideshow with only required fields."""
        self.client.force_authenticate(user=self.teacher)
        data = {
            "title": "Minimal Slideshow",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Minimal Slideshow")
        self.assertEqual(response.data["visibility"], "private")  # Default
        self.assertFalse(response.data["is_published"])  # Default
