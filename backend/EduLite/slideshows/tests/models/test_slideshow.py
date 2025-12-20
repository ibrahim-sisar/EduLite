# Unit tests for the Slideshow model

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from slideshows.models import Slideshow

User = get_user_model()


class SlideshowModelTest(TestCase):
    """
    Test the Slideshow model including creation, update, deletion, defaults,
    field constraints, and validation logic.
    """

    @classmethod
    def setUpTestData(cls):
        """Create test user for slideshow tests"""
        cls.user = User.objects.create_user(
            username="test_user", email="user@test.com", password="testpass123"
        )
        cls.other_user = User.objects.create_user(
            username="other_user", email="other@test.com", password="testpass123"
        )

    def test_slideshow_creation(self):
        """Test creating a slideshow with all fields"""
        slideshow = Slideshow.objects.create(
            title="Introduction to Python",
            description="Basic Python programming concepts",
            created_by=self.user,
            visibility="public",
            language="en",
            country="US",
            subject="computer_science",
            is_published=True,
        )

        self.assertEqual(slideshow.title, "Introduction to Python")
        self.assertEqual(slideshow.description, "Basic Python programming concepts")
        self.assertEqual(slideshow.created_by, self.user)
        self.assertEqual(slideshow.visibility, "public")
        self.assertEqual(slideshow.language, "en")
        self.assertEqual(slideshow.country, "US")
        self.assertEqual(slideshow.subject, "computer_science")
        self.assertTrue(slideshow.is_published)
        self.assertEqual(slideshow.version, 1)

    def test_slideshow_minimal_creation(self):
        """Test creating a slideshow with only required fields"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
        )

        self.assertEqual(slideshow.title, "Test Slideshow")
        self.assertEqual(slideshow.created_by, self.user)
        self.assertEqual(slideshow.visibility, "private")  # Default
        self.assertFalse(slideshow.is_published)  # Default
        self.assertIsNone(slideshow.language)
        self.assertIsNone(slideshow.country)
        self.assertIsNone(slideshow.subject)

    def test_title_validation_empty(self):
        """Test that empty title raises ValidationError"""
        slideshow = Slideshow(
            title="   ",  # Only spaces
            created_by=self.user,
        )

        with self.assertRaises(ValidationError) as context:
            slideshow.full_clean()

        self.assertIn("Title cannot be all spaces", str(context.exception))

    def test_version_defaults_to_one(self):
        """Test that version field defaults to 1"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
        )

        self.assertEqual(slideshow.version, 1)

    def test_is_published_defaults_false(self):
        """Test that is_published defaults to False"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
        )

        self.assertFalse(slideshow.is_published)

    def test_visibility_defaults_to_private(self):
        """Test that visibility defaults to private"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
        )

        self.assertEqual(slideshow.visibility, "private")

    def test_str_method(self):
        """Test the __str__ method returns the title"""
        slideshow = Slideshow.objects.create(
            title="Python Basics",
            created_by=self.user,
        )

        self.assertEqual(str(slideshow), "Python Basics")

    def test_created_by_relationship(self):
        """Test ForeignKey relationship with User"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
        )

        self.assertEqual(slideshow.created_by, self.user)
        self.assertIn(slideshow, self.user.created_slideshows.all())

    def test_cascade_delete_with_user(self):
        """Test that slideshow is deleted when user is deleted"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
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
            created_by=self.user,
        )

        slideshow2 = Slideshow.objects.create(
            title="Newer Slideshow",
            created_by=self.user,
        )

        slideshows = list(Slideshow.objects.all())
        self.assertEqual(slideshows[0], slideshow2)  # Newer first
        self.assertEqual(slideshows[1], slideshow1)

    def test_visibility_choices(self):
        """Test that all visibility choices are valid"""
        for visibility_value, _ in [
            ("public", "Public"),
            ("private", "Private"),
            ("unlisted", "Unlisted"),
        ]:
            slideshow = Slideshow.objects.create(
                title=f"Test {visibility_value}",
                created_by=self.user,
                visibility=visibility_value,
            )
            self.assertEqual(slideshow.visibility, visibility_value)

    def test_language_field_optional(self):
        """Test that language field can be null"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
            language=None,
        )
        self.assertIsNone(slideshow.language)

    def test_country_field_optional(self):
        """Test that country field can be null"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
            country=None,
        )
        self.assertIsNone(slideshow.country)

    def test_subject_field_optional(self):
        """Test that subject field can be null"""
        slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            created_by=self.user,
            subject=None,
        )
        self.assertIsNone(slideshow.subject)

    def test_multiple_users_slideshows(self):
        """Test that different users can have their own slideshows"""
        slideshow1 = Slideshow.objects.create(
            title="User 1 Slideshow",
            created_by=self.user,
        )
        slideshow2 = Slideshow.objects.create(
            title="User 2 Slideshow",
            created_by=self.other_user,
        )

        self.assertEqual(self.user.created_slideshows.count(), 1)
        self.assertEqual(self.other_user.created_slideshows.count(), 1)
        self.assertIn(slideshow1, self.user.created_slideshows.all())
        self.assertIn(slideshow2, self.other_user.created_slideshows.all())
