from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import User
from .models_choices import NOTIFICATION_TYPE_CHOICES


class Notification(models.Model):
    """
    Represents a notification sent to a user.

    Attributes:
        recipient (User): The user who received the notification.
        actor (User): The user who triggered the notification.
        verb (str): The action that triggered the notification.
        notification_type (str): The type of notification.
        is_read (bool): Whether the notification has been read.
        created_at (datetime): The date and time the notification was created.
        target_content_type (ContentType): The content type of the target object.
        target_object_id (int): The ID of the target object.
        target (GenericForeignKey): The target object of the notification.
    """
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications", db_index=True
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_notifications",
    )
    verb = models.TextField(max_length=255)
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPE_CHOICES, db_index=True
    )
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # --- Generic Foreign Key Fields ---
    # The next three fields work together to create a "Generic Foreign Key".
    # This allows a Notification to be linked to *any* model in our project
    # (e.g., a FriendRequest, a ChatRoom, an Assignment)
    target_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    description = models.TextField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
            """
            Provides a detailed and readable string representation of the notification.
            """
            # Start with the read status
            status = "[Read]" if self.is_read else "[Unread]"

            # Build the core message
            message = f"Notification for {self.recipient.username}"

            # Add the actor if one exists
            if self.actor:
                message += f" from {self.actor.username}"

            # Add the verb
            message += f": '{self.verb}'"

            # Add the target if it exists
            if self.target:
                message += f" (Target: {self.target})"

            return f"{status} {message}"
