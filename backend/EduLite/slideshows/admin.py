from django.contrib import admin
from .models import Slideshow, Slide


class SlideInline(admin.TabularInline):
    """Inline admin for editing slides within a slideshow"""

    model = Slide
    extra = 1
    fields = ("order", "content")
    ordering = ["order"]


@admin.register(Slideshow)
class SlideshowAdmin(admin.ModelAdmin):
    """Admin interface for Slideshow model"""

    list_display = (
        "title",
        "created_by",
        "visibility",
        "subject",
        "is_published",
        "version",
        "updated_at",
    )
    list_filter = (
        "is_published",
        "visibility",
        "subject",
        "language",
        "country",
        "created_at",
    )
    search_fields = ("title", "description", "created_by__username")
    readonly_fields = ("created_at", "updated_at", "version")
    inlines = [SlideInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "created_by",
                    "is_published",
                    "visibility",
                )
            },
        ),
        (
            "Categorization",
            {
                "fields": ("subject", "language", "country"),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("version", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    """Admin interface for individual Slide management"""

    list_display = ("slideshow", "order", "updated_at")
    list_filter = ("slideshow",)
    search_fields = ("content", "slideshow__title")
    readonly_fields = ("rendered_content", "created_at", "updated_at")
    ordering = ["slideshow", "order"]

    fieldsets = (
        (
            None,
            {"fields": ("slideshow", "order")},
        ),
        (
            "Content",
            {"fields": ("content",)},
        ),
        (
            "Rendered",
            {
                "fields": ("rendered_content",),
                "classes": ("collapse",),
                "description": "Automatically generated HTML from markdown",
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
