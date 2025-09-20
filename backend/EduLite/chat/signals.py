from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChatRoomInvitation
from notifications.models import Notification  # Adjust if needed


@receiver(post_save, sender=ChatRoomInvitation)
def notify_user_on_invitation(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.invitee,
            actor=instance.invited_by,
            verb=f"invited you to the chat room '{instance.chat_room.name}'",
            target=instance,
        )
