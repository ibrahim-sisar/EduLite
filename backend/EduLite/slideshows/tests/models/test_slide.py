# Unit tests for the Slide model

from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from courses.models import Course
from slideshows.models import Slideshow, Slide

User = get_user_model()


class SlideModelTest(TestCase):
    """
    Test the Slide model including creation, rendering, title extraction,
    ordering, and constraints.
    """

    @classmethod
    def setUpTestData(cls):
        """Create test user, course, and slideshow for slide tests"""
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

        cls.slideshow = Slideshow.objects.create(
            title="Test Slideshow",
            course=cls.course,
            created_by=cls.user,
        )

    def test_slide_creation(self):
        """Test creating a slide with all fields"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            title="Introduction",
            content="# Welcome\n\nThis is the first slide.",
            notes="Remember to introduce yourself",
        )

        self.assertEqual(slide.slideshow, self.slideshow)
        self.assertEqual(slide.order, 0)
        self.assertEqual(slide.title, "Introduction")
        self.assertIn("Welcome", slide.content)
        self.assertEqual(slide.notes, "Remember to introduce yourself")

    def test_markdown_rendering_on_save(self):
        """Test that markdown is rendered to HTML when slide is saved"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="# Hello World\n\nThis is **bold** text.",
        )

        # Check that rendered_content is populated
        self.assertIsNotNone(slide.rendered_content)
        self.assertIn("<h1", slide.rendered_content)
        self.assertIn("Hello World", slide.rendered_content)
        self.assertIn("<strong>bold</strong>", slide.rendered_content)

    def test_spellblock_alert_renders(self):
        """Test that Spellbook alert component renders correctly"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="{~ alert type='info' ~}\nThis is an alert\n{~~}",
        )

        # Check that Spellbook processed the alert
        self.assertIsNotNone(slide.rendered_content)
        # Spellbook should render alert component (exact HTML depends on Spellbook version)
        self.assertIn("alert", slide.rendered_content.lower())

    def test_spellblock_card_renders(self):
        """Test that Spellbook card component renders correctly"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="{~ card title='Test Card' ~}\nCard content\n{~~}",
        )

        # Check that Spellbook processed the card
        self.assertIsNotNone(slide.rendered_content)
        self.assertIn("card", slide.rendered_content.lower())

    def test_get_title_explicit(self):
        """Test get_title() returns explicit title when set"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            title="Explicit Title",
            content="# Some Header\n\nContent here.",
        )

        self.assertEqual(slide.get_title(), "Explicit Title")

    def test_get_title_from_h1(self):
        """Test get_title() extracts title from first H1 when no explicit title"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="# Extracted Title\n\nThis is the content.",
        )

        self.assertEqual(slide.get_title(), "Extracted Title")

    def test_get_title_from_h1_strips_html(self):
        """Test get_title() strips HTML tags from extracted title"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="# Title with **bold** and *italic*\n\nContent.",
        )

        title = slide.get_title()
        # Should extract text without HTML tags
        self.assertNotIn("<strong>", title)
        self.assertNotIn("<em>", title)
        self.assertIn("Title", title)

    def test_get_title_fallback(self):
        """Test get_title() returns 'Slide N' when no title or H1"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=5,
            content="Just some content without a heading.",
        )

        self.assertEqual(slide.get_title(), "Slide 6")  # order + 1

    def test_ordering_by_order_field(self):
        """Test that slides are ordered by order field"""
        slide2 = Slide.objects.create(
            slideshow=self.slideshow,
            order=1,
            content="Second slide",
        )

        slide1 = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="First slide",
        )

        slide3 = Slide.objects.create(
            slideshow=self.slideshow,
            order=2,
            content="Third slide",
        )

        slides = list(Slide.objects.all())
        self.assertEqual(slides[0], slide1)
        self.assertEqual(slides[1], slide2)
        self.assertEqual(slides[2], slide3)

    def test_unique_order_per_slideshow(self):
        """Test that order auto-increments to avoid conflicts when not specified"""
        slide1 = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="First slide",
        )

        # Creating without specifying order should auto-increment
        slide2 = Slide.objects.create(
            slideshow=self.slideshow,
            # order not specified - should auto-increment to 1
            content="Second slide",
        )

        slide2.refresh_from_db()
        self.assertEqual(slide2.order, 1)

        # But explicitly setting to an existing order should still fail
        with self.assertRaises(IntegrityError):
            Slide.objects.create(
                slideshow=self.slideshow,
                order=0,  # Explicitly duplicate order
                content="Conflicting slide",
            )

    def test_order_can_be_same_across_slideshows(self):
        """Test that order can be the same across different slideshows"""
        slideshow2 = Slideshow.objects.create(
            title="Second Slideshow",
            course=self.course,
            created_by=self.user,
        )

        slide1 = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="Slide in first slideshow",
        )

        # Should not raise error (different slideshow)
        slide2 = Slide.objects.create(
            slideshow=slideshow2,
            order=0,  # Same order, different slideshow
            content="Slide in second slideshow",
        )

        self.assertEqual(slide1.order, slide2.order)
        self.assertNotEqual(slide1.slideshow, slide2.slideshow)

    def test_str_method(self):
        """Test the __str__ method returns expected format"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            title="Test Slide",
            content="Content",
        )

        expected = f"{self.slideshow.title} - Test Slide"
        self.assertEqual(str(slide), expected)

    def test_cascade_delete_with_slideshow(self):
        """Test that slide is deleted when slideshow is deleted"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="Test content",
        )

        slide_id = slide.id
        self.slideshow.delete()

        with self.assertRaises(Slide.DoesNotExist):
            Slide.objects.get(id=slide_id)

    def test_timestamps_auto_set(self):
        """Test that created_at and updated_at are automatically set"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            order=0,
            content="Test content",
        )

        self.assertIsNotNone(slide.created_at)
        self.assertIsNotNone(slide.updated_at)

    def test_auto_increment_order_for_new_slides(self):
        """Test that order auto-increments when not specified"""
        # Create first slide without specifying order
        slide1 = Slide.objects.create(
            slideshow=self.slideshow,
            content="First slide",
        )

        # Create second slide without specifying order
        slide2 = Slide.objects.create(
            slideshow=self.slideshow,
            content="Second slide",
        )

        # Create third slide without specifying order
        slide3 = Slide.objects.create(
            slideshow=self.slideshow,
            content="Third slide",
        )

        # Verify orders were auto-assigned sequentially
        self.assertEqual(slide1.order, 0)
        self.assertEqual(slide2.order, 1)
        self.assertEqual(slide3.order, 2)

    def test_explicit_order_not_overridden(self):
        """Test that explicit order values are respected"""
        # Create slide with explicit non-zero order
        slide1 = Slide.objects.create(
            slideshow=self.slideshow,
            order=5,  # Explicit order
            content="Slide with explicit order",
        )

        self.assertEqual(slide1.order, 5)

        # Next auto-assigned slide should be 6 (max + 1)
        slide2 = Slide.objects.create(
            slideshow=self.slideshow,
            content="Auto-assigned after explicit",
        )

        self.assertEqual(slide2.order, 6)

    def test_auto_increment_starts_at_zero_for_first_slide(self):
        """Test that first slide gets order=0 when auto-assigned"""
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            content="First slide",
        )

        self.assertEqual(slide.order, 0)

    def test_auto_increment_continues_after_gap(self):
        """Test that auto-increment uses max + 1 even with gaps"""
        # Create slides with specific orders, leaving gaps
        Slide.objects.create(slideshow=self.slideshow, order=0, content="Slide 0")
        Slide.objects.create(slideshow=self.slideshow, order=5, content="Slide 5")
        Slide.objects.create(slideshow=self.slideshow, order=10, content="Slide 10")

        # Auto-assigned should be 11 (max + 1)
        slide = Slide.objects.create(
            slideshow=self.slideshow,
            content="Auto-assigned",
        )

        self.assertEqual(slide.order, 11)
