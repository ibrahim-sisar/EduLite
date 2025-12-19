# Contains slideshow and slide models for markdown-based presentations

import re
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Slideshow(models.Model):
    """
    A markdown-based slideshow presentation belonging to a course.
    Teachers create and edit, students view when published.
    """

    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        help_text="Title of the slideshow presentation",
    )

    description = models.TextField(
        blank=True,
        null=True,
        max_length=1000,
        help_text="Brief description of the slideshow content",
    )

    # Relationships
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="slideshows",
        help_text="The course this slideshow belongs to",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_slideshows",
        help_text="The teacher who created this slideshow",
    )

    # State management
    is_published = models.BooleanField(
        default=False, help_text="Whether the slideshow is visible to students"
    )

    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for conflict resolution (last-write-wins)",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["course", "-updated_at"]),
            models.Index(fields=["created_by", "-updated_at"]),
            models.Index(fields=["is_published", "course"]),
        ]
        verbose_name = "Slideshow"
        verbose_name_plural = "Slideshows"

    def clean(self):
        super().clean()
        if not self.title.strip():
            raise ValidationError("Title cannot be all spaces")

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Slide(models.Model):
    """
    Individual slide within a slideshow.
    Markdown content rendered server-side via Django Spellbook.
    """

    # Relationship
    slideshow = models.ForeignKey(
        Slideshow,
        on_delete=models.CASCADE,
        related_name="slides",
        help_text="The slideshow this slide belongs to",
    )

    # Ordering
    order = models.PositiveIntegerField(
        default=0, help_text="Display order within the slideshow (0-indexed)"
    )

    # Content
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional slide title (if empty, extracted from first H1 or 'Slide {order}')",
    )

    content = models.TextField(help_text="Markdown content with SpellBlock support")

    # Rendered HTML (cached on save)
    rendered_content = models.TextField(
        blank=True, help_text="Cached HTML rendered from markdown via Spellbook"
    )

    # Speaker notes (teachers only)
    notes = models.TextField(
        blank=True, null=True, help_text="Speaker notes visible only to teachers"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["slideshow", "order"]),
        ]
        unique_together = [["slideshow", "order"]]
        verbose_name = "Slide"
        verbose_name_plural = "Slides"

    def save(self, *args, **kwargs):
        """Render markdown to HTML on save"""
        from django_spellbook.parsers import spellbook_render

        self.rendered_content = spellbook_render(self.content)
        super().save(*args, **kwargs)

    def get_title(self):
        """
        Get slide title: explicit title, or extracted from first H1, or fallback
        """
        if self.title:
            return self.title

        # Try to extract from first H1 in rendered content
        match = re.search(r"<h1[^>]*>(.*?)</h1>", self.rendered_content)
        if match:
            # Strip HTML tags from title
            title = re.sub(r"<[^>]+>", "", match.group(1))
            return title.strip()

        # Fallback
        return f"Slide {self.order + 1}"

    def __str__(self):
        return f"{self.slideshow.title} - {self.get_title()}"
