from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    """
    Represents a chat room or conversation between users.
    Can be one-to-one or group chat.
    """

    ROOM_TYPES = (
        ("ONE_TO_ONE", "One to One"),
        ("GROUP", "Group"),
        ("COURSE", "Course Group"),
    )

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="created_chat_rooms", null=True, blank=True)
    editors = models.ManyToManyField(User, related_name="edited_chat_rooms", blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    def is_creator(self, user):
        """Check if user is the creator of this room"""
        return self.creator == user

    def is_editor(self, user):
        """Check if user is an editor of this room"""
        return self.editors.filter(id=user.id).exists()

    def can_manage(self, user):
        """Check if user can manage this room"""
        return self.is_creator(user) or self.is_editor(user)

    def __str__(self):
        return self.name or f"Chat {self.id}"


class Message(models.Model):
    """
    Represents a message sent in a chat room.
    Each message is associated with a chat room and a sender.
    """
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."
