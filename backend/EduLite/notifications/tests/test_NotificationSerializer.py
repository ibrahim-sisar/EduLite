# backend/EduLite/notifications/tests/test_NotificationSerializer.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIRequestFactory

from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from users.models import UserProfile, ProfileFriendRequest

User = get_user_model()


class NotificationSerializerTests(TestCase):
    """
    Test suite for the NotificationSerializer.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified objects used by all test methods.
        """
        # Create users
        cls.recipient_user = User.objects.create_user(
            username="recipient",
            email="recipient@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith",
        )

        cls.actor_user = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )

        # Get user profiles (assuming signals create them)
        cls.recipient_profile = UserProfile.objects.get(user=cls.recipient_user)
        cls.actor_profile = UserProfile.objects.get(user=cls.actor_user)

        # Create a target object for testing GenericForeignKey
        cls.friend_request = ProfileFriendRequest.objects.create(
            sender=cls.actor_profile, receiver=cls.recipient_profile
        )

        # APIRequestFactory for context
        cls.factory = APIRequestFactory()

    def test_serializer_contains_expected_fields(self):
        """
        Test that the serializer output contains all expected fields.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            actor=self.actor_user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
            target=self.friend_request,
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        expected_keys = [
            "id",
            "actor_details",
            "verb",
            "notification_type",
            "is_read",
            "created_at",
            "target_details",
        ]
        self.assertEqual(set(data.keys()), set(expected_keys))

    def test_notification_with_actor_and_target(self):
        """
        Test serialization of notification with actor and target.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            actor=self.actor_user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
            target=self.friend_request,
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Test basic fields
        self.assertEqual(data["id"], notification.id)
        self.assertEqual(data["verb"], "sent you a friend request")
        self.assertEqual(data["notification_type"], "FRIEND_REQUEST")
        self.assertFalse(data["is_read"])

        # Test actor_details (should use BasicUserSerializer)
        self.assertIsInstance(data["actor_details"], dict)
        self.assertEqual(data["actor_details"]["id"], self.actor_user.id)
        self.assertEqual(data["actor_details"]["username"], "actor")
        self.assertEqual(data["actor_details"]["first_name"], "John")
        self.assertEqual(data["actor_details"]["last_name"], "Doe")

        # Test target_details
        self.assertIsInstance(data["target_details"], dict)
        self.assertEqual(data["target_details"]["type"], "profilefriendrequest")
        self.assertEqual(data["target_details"]["id"], self.friend_request.id)
        self.assertEqual(data["target_details"]["display"], str(self.friend_request))

    def test_notification_without_actor(self):
        """
        Test serialization of system notification without actor.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb="System maintenance will occur tonight",
            notification_type="SYSTEM_ANNOUNCEMENT",
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        self.assertEqual(data["verb"], "System maintenance will occur tonight")
        self.assertEqual(data["notification_type"], "SYSTEM_ANNOUNCEMENT")
        self.assertIsNone(data["actor_details"])

    def test_notification_without_target(self):
        """
        Test serialization of notification without target object.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            actor=self.actor_user,
            verb="updated their profile",
            notification_type="FRIEND_REQUEST",
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Test target_details when no target
        expected_target_details = {
            "type": None,
            "id": None,
            "display": None,
        }
        self.assertEqual(data["target_details"], expected_target_details)

    def test_notification_with_deleted_target(self):
        """
        Test serialization when target object has been deleted.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            actor=self.actor_user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
            target=self.friend_request,
        )

        # Delete the target object
        target_id = self.friend_request.id
        self.friend_request.delete()

        # Refresh notification from database
        notification.refresh_from_db()

        serializer = NotificationSerializer(notification)
        data = serializer.data

        # When target is deleted, obj.target should be None
        expected_target_details = {
            "type": None,
            "id": None,
            "display": None,
        }
        self.assertEqual(data["target_details"], expected_target_details)

    def test_created_at_field_format(self):
        """
        Test the created_at field format matches expected pattern.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb="Test notification",
            notification_type="SYSTEM_ANNOUNCEMENT",
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Check format (YYYY-MM-DD HH:MM:SS)
        self.assertIsInstance(data["created_at"], str)
        self.assertRegex(data["created_at"], r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_read_only_fields(self):
        """
        Test that all specified fields are read-only.
        """
        meta_read_only = getattr(NotificationSerializer.Meta, "read_only_fields", [])
        expected_read_only = [
            "id",
            "actor_details",
            "verb",
            "notification_type",
            "created_at",
            "target_details",
        ]

        for field in expected_read_only:
            self.assertIn(
                field, meta_read_only, f"Field '{field}' should be in read_only_fields"
            )

    def test_is_read_field_modifiable(self):
        """
        Test that is_read field is not in read_only_fields (can be modified).
        """
        meta_read_only = getattr(NotificationSerializer.Meta, "read_only_fields", [])
        self.assertNotIn(
            "is_read", meta_read_only, "Field 'is_read' should not be read-only"
        )

    def test_multiple_notifications_serialization(self):
        """
        Test serialization of multiple notifications (many=True).
        """
        notification1 = Notification.objects.create(
            recipient=self.recipient_user,
            actor=self.actor_user,
            verb="sent you a friend request",
            notification_type="FRIEND_REQUEST",
        )

        notification2 = Notification.objects.create(
            recipient=self.recipient_user,
            verb="System update available",
            notification_type="SYSTEM_ANNOUNCEMENT",
        )

        notifications = [notification1, notification2]
        serializer = NotificationSerializer(notifications, many=True)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["verb"], "sent you a friend request")
        self.assertEqual(data[1]["verb"], "System update available")

    def test_target_details_with_different_model_types(self):
        """
        Test target_details handling with different target model types.
        """
        # Test with User as target
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            actor=self.actor_user,
            verb="mentioned you",
            notification_type="NEW_MESSAGE",
            target=self.actor_user,  # Using User as target
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        self.assertEqual(data["target_details"]["type"], "user")
        self.assertEqual(data["target_details"]["id"], self.actor_user.id)
        self.assertEqual(data["target_details"]["display"], str(self.actor_user))

    def test_serializer_excludes_recipient(self):
        """
        Test that recipient field is not included in serialized output.
        This is intentional since recipient will be filtered by views.
        """
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb="Test notification",
            notification_type="SYSTEM_ANNOUNCEMENT",
        )

        serializer = NotificationSerializer(notification)
        data = serializer.data

        self.assertNotIn(
            "recipient",
            data.keys(),
            "Recipient field should not be in serialized output",
        )
        self.assertNotIn(
            "recipient_id",
            data.keys(),
            "Recipient ID should not be in serialized output",
        )

    def test_get_target_details_method_type_hints(self):
        """
        Test that get_target_details method exists and has proper signature.
        """
        # This test ensures the method exists and can be called
        notification = Notification.objects.create(
            recipient=self.recipient_user,
            verb="Test notification",
        )

        serializer = NotificationSerializer()
        result = serializer.get_target_details(notification)

        # Should return a dict with expected keys
        self.assertIsInstance(result, dict)
        expected_keys = ["type", "id", "display"]
        self.assertEqual(set(result.keys()), set(expected_keys))
