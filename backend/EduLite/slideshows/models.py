# Contains slideshow and slide models for markdown-based presentations

import re
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .model_choices import (
    SLIDESHOW_VISIBILITY_CHOICES,
    LANGUAGE_CHOICES,
    COUNTRY_CHOICES,
    SUBJECT_CHOICES,
)

User = get_user_model()


class Slideshow(models.Model):
    """
    A standalone markdown-based slideshow presentation.

    Slideshows are created and owned by users independently.
    They can optionally be attached to courses via CourseModule's GenericForeignKey.

    Visibility controls who can view the slideshow:
    - public: Discoverable and viewable by anyone (if published)
    - unlisted: Not discoverable, but viewable with direct link (if published)
    - private: Only the owner can view

    The is_published flag controls draft vs ready state:
    - False: Draft mode, only owner can view regardless of visibility
    - True: Ready for viewing, respects visibility settings
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

    # Ownership (replaces course-based permissions)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_slideshows",
        help_text="The user who created this slideshow",
    )

    # Visibility & discoverability
    visibility = models.CharField(
        max_length=64,
        choices=SLIDESHOW_VISIBILITY_CHOICES,
        default="private",
        help_text="Who can view this slideshow (public/unlisted/private)",
    )

    # Metadata for organization and search
    language = models.CharField(
        max_length=64,
        choices=LANGUAGE_CHOICES,
        blank=True,
        null=True,
        help_text="Primary language of the slideshow content",
    )

    country = models.CharField(
        max_length=64,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        help_text="Country/region this content is relevant to",
    )

    subject = models.CharField(
        max_length=64,
        choices=SUBJECT_CHOICES,
        blank=True,
        null=True,
        help_text="Subject area of the slideshow",
    )

    # State management
    is_published = models.BooleanField(
        default=False,
        help_text="Whether the slideshow is ready for viewing (draft vs published)",
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
            models.Index(fields=["created_by", "-updated_at"]),
            models.Index(fields=["visibility", "-updated_at"]),
            models.Index(fields=["subject", "-updated_at"]),
            models.Index(fields=["is_published", "visibility"]),
        ]
        verbose_name = "Slideshow"
        verbose_name_plural = "Slideshows"

    def clean(self):
        super().clean()
        if not self.title.strip():
            raise ValidationError("Title cannot be all spaces")

    def __str__(self):
        return self.title


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
        default=None,
        null=True,
        blank=True,
        help_text="Display order within the slideshow (leave blank to auto-assign next available order)",
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

    # Speaker notes (owner only)
    notes = models.TextField(
        blank=True, null=True, help_text="Speaker notes visible only to slideshow owner"
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
        """Render markdown to HTML and auto-assign order on save"""
        # Auto-assign order for new slides if not explicitly set
        if self.pk is None and self.order is None:
            # Get current max order for this slideshow
            max_order = Slide.objects.filter(slideshow=self.slideshow).aggregate(
                models.Max("order")
            )["order__max"]

            # Assign next available order (0 if no slides exist)
            self.order = (max_order + 1) if max_order is not None else 0

        # Render markdown to HTML
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
