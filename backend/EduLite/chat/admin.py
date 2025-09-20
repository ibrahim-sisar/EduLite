from django.contrib import admin
from .models import ChatRoom, Message, ChatRoomInvitation


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "room_type", "created_at")
    list_filter = ("room_type", "created_at")
    search_fields = ("name", "participants__username")
    filter_horizontal = ("participants",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat_room",
        "sender",
        "short_content",
        "created_at",
        "is_read",
    )
    list_filter = ("is_read", "created_at", "sender")
    search_fields = ("content", "sender__username", "chat_room__name")

    def short_content(self, obj):
        """Display a shortened version of the message content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    short_content.short_description = "Content Preview"


@admin.register(ChatRoomInvitation)
class ChatRoomInvitationAdmin(admin.ModelAdmin):
    list_display = ("chat_room", "invited_by", "invitee", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("chat_room__name", "invited_by__username", "invitee__username")
