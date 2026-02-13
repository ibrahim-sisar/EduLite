from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Course, CourseChatRoom, CourseMembership, CourseModule

# --- Inlines: Making the UI much faster to use ---
# These let us edit modules and members directly inside the Course page,
# so we don't have to jump around between different pages.


class CourseModuleInline(admin.TabularInline):
    """Allows adding/editing modules directly on the Course detail page."""

    model = CourseModule
    fields = ("order", "title", "content_type", "object_id")
    extra = 1  # Shows one empty row by default for quick adding


class CourseMembershipInline(admin.TabularInline):
    """Lets us manage students/teachers directly from the Course page."""

    model = CourseMembership
    fields = ("user", "role", "status")
    extra = 1


# --- Model Admins: Crafting the Dashboard experience ---


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # This controls the "Spreadsheet" view (the list of all courses)
    list_display = ("title", "visibility", "is_active", "start_date", "subject")

    # Adding filters to the right sidebar so admins can drill down
    list_filter = ("visibility", "is_active", "subject", "language", "country")

    # Let's make it searchable by title and the outline text
    search_fields = ("title", "outline")

    # Grouping the fields into "buckets" to make the form less overwhelming
    fieldsets = (
        (
            "Core Information",
            {"fields": ("title", "outline", "subject", "language", "country")},
        ),
        ("Access Control", {"fields": ("visibility", "is_active")}),
        ("Timeline", {"fields": ("start_date", "end_date")}),
    )

    # Hooking up the inlines we defined above
    inlines = [CourseModuleInline, CourseMembershipInline]

    def save_related(self, request, form, formsets, change):
        """Enforce that every course has at least one enrolled teacher after saving inlines."""
        super().save_related(request, form, formsets, change)
        course = form.instance
        has_teacher = CourseMembership.objects.filter(
            course=course, role="teacher", status="enrolled"
        ).exists()
        if not has_teacher:
            raise ValidationError("A course must have at least one enrolled teacher.")


@admin.register(CourseMembership)
class CourseMembershipAdmin(admin.ModelAdmin):
    """A dedicated view for managing user enrollments."""

    list_display = ("user", "course", "role", "status")
    list_filter = ("role", "status", "course")
    search_fields = ("user__username", "course__title")


@admin.register(CourseChatRoom)
class CourseChatRoomAdmin(admin.ModelAdmin):
    """Specific settings for the course chat functionality."""

    list_display = ("course", "chatroom", "created_by")
    list_filter = ("course",)

    # Security: We don't want admins accidentally changing who created a room
    readonly_fields = ("created_by",)
