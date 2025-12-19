# Unit tests for the Slideshow model

from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from courses.models import Course
from slideshows.models import Slideshow

User = get_user_model()


class SlideshowModelTest(TestCase):
    """
    Test the Slideshow model including creation, update, deletion, defaults,
    field constraints, and validation logic.
    """

    @classmethod
    def setUpTestData(cls):
        """Create test user and course for slideshow tests"""
        cls.user = User.objects.create_user(
            username="test_teacher", email="teacher@test.com", password="testpass123"
        )

        cls.course = Course.objects.create(
            title="Test Course",
            outline="Test course outline",
            language="en",
            country="US",
            subject="physics",
            visibility="public",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=90),
            is_active=True,
        )

    def test_slideshow_creation(self):
        """Test creating a slideshow with all required fields"""
        slideshow = Slideshow.objects.create(
            title="Introduction to Python",
            description="Basic Python programming concepts",
            course=self.course,
            created_by=self.user,
            is_published=True,
        )

        self.assertEqual(slideshow.title, "Introduction to Python")
        self.assertEqual(slideshow.description, "Basic Python programming concepts")
        self.assertEqual(slideshow.course, self.course)
        self.assertEqual(slideshow.created_by, self.user)
        self.assertTrue(slideshow.is_published)
        self.assertEqual(slideshow.version, 1)

    def test_title_validation_empty(self):
        """Test that empty title raises ValidationError"""
        slideshow = Slideshow(
            title="   ",  # Only spaces
            course=self.course,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError) as context:
            slideshow.full_clean()

        self.assertIn("Title cannot be all spaces", str(context.exception))

    def test_version_defaults_to_one(self):
        """Test that version field defaults to 1"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        self.assertEqual(slideshow.version, 1)

    def test_is_published_defaults_false(self):
        """Test that is_published defaults to False"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        self.assertFalse(slideshow.is_published)

    def test_str_method(self):
        """Test the __str__ method returns expected format"""
        slideshow = Slideshow.objects.create(
            title="Python Basics",
            course=self.course,
            created_by=self.user,
        )

        expected = f"Python Basics - {self.course.title}"
        self.assertEqual(str(slideshow), expected)

    def test_course_relationship(self):
        """Test ForeignKey relationship with Course"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        self.assertEqual(slideshow.course, self.course)
        self.assertIn(slideshow, self.course.slideshows.all())

    def test_created_by_relationship(self):
        """Test ForeignKey relationship with User"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        self.assertEqual(slideshow.created_by, self.user)
        self.assertIn(slideshow, self.user.created_slideshows.all())

    def test_cascade_delete_with_course(self):
        """Test that slideshow is deleted when course is deleted"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        slideshow_id = slideshow.id
        self.course.delete()

        with self.assertRaises(Slideshow.DoesNotExist):
            Slideshow.objects.get(id=slideshow_id)

    def test_cascade_delete_with_user(self):
        """Test that slideshow is deleted when user is deleted"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        slideshow_id = slideshow.id
        self.user.delete()

        with self.assertRaises(Slideshow.DoesNotExist):
            Slideshow.objects.get(id=slideshow_id)

    def test_timestamps_auto_set(self):
        """Test that created_at and updated_at are automatically set"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=self.course,
            created_by=self.user,
        )

        self.assertIsNotNone(slideshow.created_at)
        self.assertIsNotNone(slideshow.updated_at)
        # created_at and updated_at should be close (within 1 second)
        time_diff = slideshow.updated_at - slideshow.created_at
        self.assertLess(time_diff.total_seconds(), 1)

    def test_ordering_by_updated_at(self):
        """Test that slideshows are ordered by updated_at descending"""
        slideshow1 = Slideshow.objects.create(
            title="Older Slideshow",
            course=self.course,
            created_by=self.user,
        )

        slideshow2 = Slideshow.objects.create(
            title="Newer Slideshow",
            course=self.course,
            created_by=self.user,
        )

        slideshows = list(Slideshow.objects.all())
        self.assertEqual(slideshows[0], slideshow2)  # Newer first
        self.assertEqual(slideshows[1], slideshow1)
