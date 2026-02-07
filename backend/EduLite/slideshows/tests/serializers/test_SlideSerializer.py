"""Tests for SlideSerializer."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from slideshows.models import Slideshow, Slide
from slideshows.serializers import SlideSerializer

User = get_user_model()


class SlideSerializerTestCase(TestCase):
    """Test cases for SlideSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create users
        self.teacher = User.objects.create_user(
            username="teacher", email="teacher@test.com", password="password123"
        )
        self.student = User.objects.create_user(
            username="student", email="student@test.com", password="password123"
        )

        # Create course        # Create memberships        # Create slideshow
        self.slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            visibility="public",
            created_by=self.teacher,
            is_published=True,
        )

        # Create slide
        self.slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="# Test Content\n\nHello world",
        )

        self.factory = APIRequestFactory()

    def test_slide_serializer_includes_rendered_content(self):
        """Test that rendered_content is always included."""
        serializer = SlideSerializer(self.slide)
        self.assertIn("rendered_content", serializer.data)
        self.assertIsNotNone(serializer.data["rendered_content"])

    def test_slide_serializer_excludes_content_for_students(self):
        """Test that raw content is excluded for students."""
        request = self.factory.get("/")
        request.user = self.student

        serializer = SlideSerializer(self.slide, context={"request": request})
        self.assertNotIn("content", serializer.data)

    def test_slide_serializer_includes_all_fields_for_teachers(self):
        """Test that teachers see all fields including content."""
        request = self.factory.get("/")
        request.user = self.teacher

        serializer = SlideSerializer(self.slide, context={"request": request})
        self.assertIn("content", serializer.data)
        self.assertIn("rendered_content", serializer.data)

    def test_slide_serializer_read_only_fields(self):
        """Test that certain fields are read-only."""
        data = {
            "order": 1,
            "content": "# Updated Content",
            "id": 999,  # Should be ignored
            "rendered_content": "<p>Fake HTML</p>",  # Should be ignored
        }
        serializer = SlideSerializer(self.slide, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        # rendered_content should not be in validated_data
        self.assertNotIn("rendered_content", serializer.validated_data)
