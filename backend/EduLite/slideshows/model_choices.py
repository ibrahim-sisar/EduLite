"""Model choices for the slideshows app."""

# Import shared choices from courses app for consistency
from courses.model_choices import (
    LANGUAGE_CHOICES,
    COUNTRY_CHOICES,
    SUBJECT_CHOICES,
)

# Slideshow-specific visibility choices
SLIDESHOW_VISIBILITY_CHOICES = [
    ("public", "Public"),  # Discoverable, anyone can view if published
    ("unlisted", "Unlisted"),  # Not discoverable, but viewable with link if published
    ("private", "Private"),  # Only owner can view
]
