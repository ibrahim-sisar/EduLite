# courses/tests/test_Course.py
# Unit tests for the Course model

from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import Course
from ..model_choices import (
    COURSE_VISIBILITY_CHOICES,
    LANGUAGE_CHOICES,
    COUNTRY_CHOICES,
    SUBJECT_CHOICES,
)


class CourseModelTest(TestCase):
    """
    Test the Course model including creation, update, deletion, defaults,
    field constraints, and validation logic.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Create several course instances with different field combinations.
        """
        cls.course1 = Course.objects.create(
            title="test_course1",
            outline="This is test_course1 outline",
            language="en",
            country="US",
            subject="physics",
            visibility="public",
            start_date=datetime(2025, 12, 31, 23, 59, 59),
            end_date=datetime(2025, 12, 31, 23, 59, 59) + timedelta(days=30),
            is_active=False,
            allow_join_requests=False,
        )

        cls.course2 = Course.objects.create(
            title="test_course2",
            outline="This is test_course2 outline",
            language="en",
            country="US",
            subject="math",
        )

        cls.course3 = Course.objects.create(
            title="test_course3",
            language="en",
            country="US",
            subject="math",
        )

        cls.course4 = Course.objects.create(title="test_course4")

    def test_course_creation(self) -> None:
        """
        Test that a course is created with all fields correctly stored.
        """
        self.assertEqual(self.course1.title, "test_course1")
        self.assertEqual(self.course1.outline, "This is test_course1 outline")
        self.assertEqual(self.course1.language, "en")
        self.assertEqual(self.course1.country, "US")
        self.assertEqual(self.course1.subject, "physics")
        self.assertEqual(self.course1.visibility, "public")
        self.assertEqual(self.course1.start_date, datetime(2025, 12, 31, 23, 59, 59))
        self.assertEqual(
            self.course1.end_date,
            datetime(2025, 12, 31, 23, 59, 59) + timedelta(days=30),
        )
        self.assertFalse(self.course1.is_active)
        self.assertFalse(self.course1.allow_join_requests)

    def test_course_default_values(self) -> None:
        """
        Test that default boolean fields are set correctly.
        """
        self.assertEqual(self.course1.visibility, "public")
        self.assertFalse(self.course1.is_active)
        self.assertFalse(self.course1.allow_join_requests)

    def test_course_delete(self) -> None:
        """
        Test that a course can be deleted.
        """
        self.course1.delete()
        self.assertEqual(Course.objects.count(), 3)

    def test_course_update(self) -> None:
        """
        Test that a course can be updated.
        """
        self.course3.title = "updated_course3"
        self.course3.save()
        self.assertEqual(self.course3.title, "updated_course3")

    def test_course_title_max_length(self) -> None:
        """
        Test that title exceeding 128 characters raises ValidationError.
        """
        self.course3.title = "x" * 129
        with self.assertRaises(ValidationError):
            self.course3.full_clean()

    def test_course_title_with_blank_values(self) -> None:
        """
        Test that a course title cannot consist of only whitespace.
        """
        self.course3.title = "    "
        with self.assertRaises(ValidationError):
            self.course3.full_clean()

    def test_course_startdate_after_enddate(self) -> None:
        """
        Test that start_date must be before end_date.
        """
        self.course1.start_date = datetime(2025, 12, 31, 23, 59, 59)
        self.course1.end_date = datetime(2025, 12, 11, 23, 59, 59)
        with self.assertRaises(ValidationError):
            self.course1.full_clean()

    def test_course_value_null(self) -> None:
        """
        Test that a course created with minimal fields has expected null/default values.
        """
        self.course4.full_clean()
        self.assertIsNone(self.course4.outline)
        self.assertIsNone(self.course4.language)
        self.assertIsNone(self.course4.country)
        self.assertIsNone(self.course4.subject)
        self.assertIsNotNone(self.course4.start_date)
        self.assertIsNotNone(self.course4.end_date)
        self.assertEqual(self.course4.visibility, "private")
        self.assertFalse(self.course4.is_active)
        self.assertFalse(self.course4.allow_join_requests)

    def test_course_can_save_choices_fields(self) -> None:
        """
        Test that all choice fields accept valid enum values.
        """
        self.course1.visibility = COURSE_VISIBILITY_CHOICES[0][0]
        self.course1.language = LANGUAGE_CHOICES[0][0]
        self.course1.country = COUNTRY_CHOICES[0][0]
        self.course1.subject = SUBJECT_CHOICES[0][0]
        self.course1.save()

        self.assertEqual(self.course1.visibility, COURSE_VISIBILITY_CHOICES[0][0])
        self.assertEqual(self.course1.language, LANGUAGE_CHOICES[0][0])
        self.assertEqual(self.course1.country, COUNTRY_CHOICES[0][0])
        self.assertEqual(self.course1.subject, SUBJECT_CHOICES[0][0])
