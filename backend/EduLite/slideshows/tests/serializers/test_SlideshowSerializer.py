"""Tests for Slideshow serializers."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from slideshows.models import Slideshow, Slide
from slideshows.serializers import (
    SlideshowListSerializer,
    SlideshowDetailSerializer,
)

User = get_user_model()


class SlideshowListSerializerTestCase(TestCase):
    """Test cases for SlideshowListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="password123"
        )

        self.slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            visibility="public",
            created_by=self.user,
            is_published=True,
        )
        # Add some slides
        for i in range(3):
            Slide.objects.create(
                slideshow=self.slideshow,
                order=i,
                content=f"# Slide {i}",
            )

    def test_slideshow_list_serializer_fields(self):
        """Test that list serializer includes correct fields."""
        serializer = SlideshowListSerializer(self.slideshow)
        expected_fields = {
            "id",
            "title",
            "description",
            "created_by",
            "created_by_username",
            "visibility",
            "language",
            "country",
            "subject",
            "is_published",
            "version",
            "slide_count",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_slideshow_list_serializer_slide_count(self):
        """Test that slide_count returns correct number."""
        serializer = SlideshowListSerializer(self.slideshow)
        self.assertEqual(serializer.data["slide_count"], 3)

    def test_slideshow_list_serializer_no_nested_slides(self):
        """Test that list serializer does not include nested slides."""
        serializer = SlideshowListSerializer(self.slideshow)
        self.assertNotIn("slides", serializer.data)


class SlideshowDetailSerializerTestCase(TestCase):
    """Test cases for SlideshowDetailSerializer."""

    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="password123"
        )

        self.slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            visibility="public",
            created_by=self.teacher,
            is_published=True,
        )
        # Add 10 slides for progressive loading tests
        for i in range(10):
            Slide.objects.create(
                slideshow=self.slideshow,
                order=i,
                content=f"# Slide {i}",
            )
        self.factory = APIRequestFactory()

    def test_slideshow_detail_serializer_nested_slides(self):
        """Test that detail serializer includes nested slides."""
        serializer = SlideshowDetailSerializer(self.slideshow)
        self.assertIn("slides", serializer.data)
        self.assertEqual(len(serializer.data["slides"]), 10)

    def test_slideshow_detail_serializer_remaining_slide_ids(self):
        """Test remaining_slide_ids with initial parameter."""
        request = self.factory.get("/?initial=3")
        request.user = self.teacher
        request.query_params = {"initial": "3"}

        serializer = SlideshowDetailSerializer(
            self.slideshow, context={"request": request}
        )
        data = serializer.data

        # Should only include first 3 slides
        self.assertEqual(len(data["slides"]), 3)
        # Should have 7 remaining slide IDs
        self.assertEqual(len(data["remaining_slide_ids"]), 7)

    def test_slideshow_detail_serializer_create_with_slides(self):
        """Test creating slideshow with nested slides."""
        request = self.factory.post("/")
        request.user = self.teacher

        data = {
            "title": "New Slideshow",
            "description": "Test description",
            "visibility": "public",
            "is_published": False,
            "slides": [
                {"order": 0, "content": "# First Slide"},
                {"order": 1, "content": "# Second Slide", "notes": "Test notes"},
            ],
        }

        serializer = SlideshowDetailSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        slideshow = serializer.save()

        self.assertEqual(slideshow.title, "New Slideshow")
        self.assertEqual(slideshow.slides.count(), 2)
        self.assertEqual(slideshow.created_by, self.teacher)

    def test_slideshow_detail_serializer_update_increments_version(self):
        """Test that updating increments version number."""
        original_version = self.slideshow.version
        data = {"title": "Updated Title"}

        serializer = SlideshowDetailSerializer(self.slideshow, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_slideshow = serializer.save()

        self.assertEqual(updated_slideshow.version, original_version + 1)

    def test_slideshow_detail_serializer_version_conflict(self):
        """Test version conflict detection."""
        request = self.factory.patch("/")
        request.user = self.teacher
        request.data = {"title": "Updated Title", "version": 999}  # Wrong version

        serializer = SlideshowDetailSerializer(
            self.slideshow,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("error", serializer.errors)
