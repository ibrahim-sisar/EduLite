from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "get_username",
        "occupation",
        "country",
        "preferred_language",
        "website_url",
        "has_profile_picture",
    )

    search_fields = (
        "user__username",
        "user__email",
        "occupation",
        "country",
        "bio",
        "website_url",
    )

    list_filter = ("occupation", "country", "preferred_language")

    readonly_fields = ("user",)

    fieldsets = (
        (
            None,
            {"fields": ("user",)},  #  # Display the linked user (read-only)
        ),
        (
            "Personal Information",
            {"fields": ("bio", "occupation", "country", "picture", "website_url")},
        ),
        (
            "Language Preferences",
            {"fields": ("preferred_language", "secondary_language")},
        ),
        ("Social Connections", {"fields": ("friends",)}),
    )

    filter_horizontal = ("friends",)  # Or filter_vertical = ('friends',)

    # Custom method to display the username in list_display
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return None

    get_username.short_description = "Username"
    get_username.admin_order_field = "user__username"

    # Custom method to display if a user has a profile picture
    def has_profile_picture(self, obj):
        return bool(obj.picture)

    has_profile_picture.boolean = True
    has_profile_picture.short_description = "Has Picture"
