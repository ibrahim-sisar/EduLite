# users/signals.py

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile, ProfileFriendRequest, UserProfilePrivacySettings

# Try to import Notification at module level
try:
    from notifications.models import Notification
except ImportError:
    Notification = None

User = get_user_model()

# Set up logger for this module
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update the user profile.
    - Creates a UserProfile instance when a new User instance is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=UserProfile)
def create_user_profile_privacy_settings(sender, instance, created, **kwargs):
    """
    Signal handler to create privacy settings for user profiles.
    - Creates a UserProfilePrivacySettings instance when a new UserProfile is created.
    """
    if created:
        try:
            UserProfilePrivacySettings.objects.create(user_profile=instance)
            logger.debug("Created privacy settings for user profile %s", instance.id)
        except Exception as e:
            logger.error(
                "Failed to create privacy settings for user profile %s: %s",
                instance.id, e
            )


@receiver(post_save, sender=ProfileFriendRequest)
def create_notification_on_friend_request(sender, instance, created, **kwargs):
    """
    Signal handler to create a notification when a friend request is sent.
    - Creates a Notification instance when a new ProfileFriendRequest is created.
    - Handles errors gracefully to prevent breaking the main friend request creation.
    """
    if not created:
        return

    try:
        # Defensive coding: Check if required objects exist
        if not instance:
            logger.warning("ProfileFriendRequest instance is None")
            return

        if not hasattr(instance, 'receiver') or not instance.receiver:
            logger.warning("ProfileFriendRequest %s has no receiver", getattr(instance, 'id', 'unknown'))
            return

        if not hasattr(instance, 'sender') or not instance.sender:
            logger.warning("ProfileFriendRequest %s has no sender", getattr(instance, 'id', 'unknown'))
            return

        if not hasattr(instance.receiver, 'user') or not instance.receiver.user:
            logger.warning("ProfileFriendRequest %s receiver has no user", instance.id)
            return

        if not hasattr(instance.sender, 'user') or not instance.sender.user:
            logger.warning("ProfileFriendRequest %s sender has no user", instance.id)
            return

        # Import here to avoid circular imports
        from notifications.models import Notification
        
        # Prepare optional message content
        description = ""
        if instance.message:
            description = f'Message: "{instance.message}"'

        Notification.objects.create(
            recipient=instance.receiver.user,
            actor=instance.sender.user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
            target=instance,
            description=description
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Notification created for friend request %s from %s to %s",
                        instance.id, instance.sender.user.username,
                        instance.receiver.user.username)

    except AttributeError as e:
        logger.error(
            "AttributeError while creating notification for friend request %s: %s",
            getattr(instance, 'id', 'unknown'), e
        )
    except Exception as e:
        # Log the error but don't re-raise it to prevent breaking the main operation
        logger.error(
            "Failed to create notification for friend request %s: %s",
            getattr(instance, 'id', 'unknown'), e
        )


@receiver(post_delete, sender=ProfileFriendRequest)
def delete_notification_on_friend_request(sender, instance, **kwargs):
    """
    Signal handler to delete a notification when a friend request is deleted.
    - Deletes the corresponding Notification instance when a ProfileFriendRequest is deleted.
    - Uses defensive coding to handle missing data gracefully.
    """
    # Store the instance ID early, as it might become None after deletion operations
    instance_id = getattr(instance, 'pk', None) or getattr(instance, 'id', 'unknown')

    try:
        # Defensive coding: Check if instance exists
        if not instance:
            logger.warning("ProfileFriendRequest instance is None in delete signal")
            return

        # Import here to avoid circular imports
        from notifications.models import Notification
        from django.contrib.contenttypes.models import ContentType

        # Get the ContentType for ProfileFriendRequest
        content_type = ContentType.objects.get_for_model(ProfileFriendRequest)

        # Find notification by content_type and object_id instead of using target
        try:
            notification = Notification.objects.get(
                target_content_type=content_type,
                target_object_id=instance_id
            )
            notification.delete()

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Deleted notification for friend request %s", instance_id)

        except ObjectDoesNotExist:
            # Notification might have been already deleted or never created
            # ObjectDoesNotExist catches all model DoesNotExist exceptions
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("No notification found for friend request %s", instance_id)

    except Exception as e:
        logger.error(
            "Failed to delete notification for friend request %s: %s",
            instance_id, e
        )
