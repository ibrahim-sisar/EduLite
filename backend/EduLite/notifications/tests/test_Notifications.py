# backend/EduLite/notifications/tests/test_Notification.py

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from users.models import User
from notifications.models import Notification


class NotificationModelTests(TestCase):
    """
    Test suite for the Notification model using Django's TestCase.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified objects used by all test methods.
        This is run once for the entire class.
        """
        cls.recipient = User.objects.create_user(
            username="testrecipient", password="password123"
        )
        cls.actor = User.objects.create_user(
            username="testactor", password="password123"
        )

    def test_notification_creation(self):
        """
        Tests that a Notification instance is created correctly.
        """
        notification = Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.recipient, self.recipient)
        self.assertEqual(notification.actor, self.actor)
        self.assertFalse(notification.is_read)

    def test_str_method_with_actor_and_target(self):
        """
        Tests the __str__ method's format with an actor and a target.
        """
        notification = Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            verb="commented on your post",
            target=self.actor,  # Using the actor as the target for this example
        )

        expected_str = (
            f"[Unread] Notification for {self.recipient.username} "
            f"from {self.actor.username}: 'commented on your post' "
            f"(Target: {self.actor})"
        )
        self.assertEqual(str(notification), expected_str)

    def test_str_method_without_actor(self):
        """
        Tests the __str__ method's format for a system notification without an actor.
        """
        notification = Notification.objects.create(
            recipient=self.recipient,
            verb="A new system update is available.",
            notification_type="SYSTEM_ANNOUNCEMENT",
        )
        notification.is_read = True
        notification.save()

        expected_str = f"[Read] Notification for {self.recipient.username}: 'A new system update is available.'"
        self.assertEqual(str(notification), expected_str)

    def test_generic_foreign_key_linking(self):
        """
        Tests that the GenericForeignKey correctly links to another object.
        """
        notification = Notification.objects.create(
            recipient=self.recipient,
            actor=self.actor,
            verb="updated their profile",
            target=self.actor,
        )
        self.assertEqual(notification.target, self.actor)
        self.assertEqual(
            notification.target_content_type, ContentType.objects.get_for_model(User)
        )
        self.assertEqual(notification.target_object_id, self.actor.id)

    def test_notification_ordering(self):
        """
        Tests that notifications are ordered by creation date, most recent first.
        """
        notification1 = Notification.objects.create(
            recipient=self.recipient, verb="First"
        )
        notification2 = Notification.objects.create(
            recipient=self.recipient, verb="Second"
        )

        notifications = list(Notification.objects.all())
        # The first item should be the most recently created one (notification2)
        self.assertEqual(notifications, [notification2, notification1])
