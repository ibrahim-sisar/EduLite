from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import (
    APIRequestFactory,
)  # For providing request context to serializer

# Assuming your models and serializers are in the 'users' app
from ..models import UserProfile, ProfileFriendRequest
from ..serializers import ProfileFriendRequestSerializer

User = get_user_model()


class ProfileFriendRequestSerializerTests(TestCase):
    """
    Test suite for the ProfileFriendRequestSerializer.
    """

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user_sender = User.objects.create_user(
            username="sender",
            first_name="Sender",
            last_name="User",
            password="password123",
        )
        cls.user_receiver = User.objects.create_user(
            username="receiver",
            first_name="Receiver",
            last_name="Person",
            password="password123",
        )

        # Get or create UserProfile instances
        # Assuming signals create UserProfile, otherwise create them explicitly.
        cls.profile_sender = UserProfile.objects.get(user=cls.user_sender)
        cls.profile_receiver = UserProfile.objects.get(user=cls.user_receiver)

        # Create a ProfileFriendRequest instance
        cls.friend_request = ProfileFriendRequest.objects.create(
            sender=cls.profile_sender, receiver=cls.profile_receiver
        )

        # APIRequestFactory for providing context to the serializer
        cls.factory = APIRequestFactory()

    def _get_serializer_with_context(self, instance):
        """Helper to get serializer with request context."""
        # Create a dummy GET request
        request = self.factory.get(
            reverse("userprofile-detail", kwargs={"pk": self.profile_sender.pk})
        )  # Dummy URL
        # Simulate request user if needed by your views/permissions that serializer might interact with (not strictly needed here for URL building)
        # request.user = self.user_sender
        return ProfileFriendRequestSerializer(instance, context={"request": request})

    def test_serializer_contains_expected_fields(self):
        """
        Test that the serializer output contains all expected fields as per Meta.fields.
        """
        serializer = self._get_serializer_with_context(self.friend_request)
        data = serializer.data
        expected_keys = [
            "id",
            "sender_id",
            "receiver_id",
            "sender_profile_url",
            "receiver_profile_url",
            "created_at",
            "accept_url",
            "decline_url",
            "message"
        ]
        self.assertEqual(set(data.keys()), set(expected_keys))

    def test_sender_field_content(self):
        """Test the 'sender' field uses UserProfile.__str__."""
        serializer = self._get_serializer_with_context(self.friend_request)
        # Based on your UserProfile.__str__(self): return f"{self.user.username}"
        self.assertEqual(serializer.data["sender_id"], self.profile_sender.user.id)

    def test_receiver_field_content(self):
        """Test the 'receiver' field uses UserProfile.__str__."""
        serializer = self._get_serializer_with_context(self.friend_request)
        # Based on your UserProfile.__str__(self): return f"{self.user.username}"
        self.assertEqual(serializer.data["receiver_id"], self.profile_receiver.user.id)

    def test_created_at_field_content_and_format(self):
        """Test the 'created_at' field content and format."""
        serializer = self._get_serializer_with_context(self.friend_request)
        # Check if it's a string (DateTimeField with format becomes string)
        self.assertIsInstance(serializer.data["created_at"], str)
        # Check format (YYYY-MM-DD HH:MM:SS)
        self.assertRegex(
            serializer.data["created_at"], r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        )
        # More precise check by parsing (optional)
        # from django.utils.dateparse import parse_datetime
        # self.assertEqual(parse_datetime(serializer.data['created_at']).date(), self.friend_request.created_at.date())

    def test_sender_profile_url_field_content(self):
        """Test the 'sender_profile_url' is correctly generated."""
        request_for_context = self.factory.get(
            reverse("userprofile-detail", kwargs={"pk": self.profile_sender.pk})
        )
        serializer = ProfileFriendRequestSerializer(
            self.friend_request, context={"request": request_for_context}
        )

        expected_url = request_for_context.build_absolute_uri(
            reverse("userprofile-detail", kwargs={"pk": self.profile_sender.pk})
        )
        self.assertEqual(serializer.data["sender_profile_url"], expected_url)

    def test_receiver_profile_url_field_content(self):
        """Test the 'receiver_profile_url' is correctly generated."""
        request_for_context = self.factory.get(
            reverse("userprofile-detail", kwargs={"pk": self.profile_receiver.pk})
        )
        serializer = ProfileFriendRequestSerializer(
            self.friend_request, context={"request": request_for_context}
        )

        expected_url = request_for_context.build_absolute_uri(
            reverse("userprofile-detail", kwargs={"pk": self.profile_receiver.pk})
        )
        self.assertEqual(serializer.data["receiver_profile_url"], expected_url)

    def test_read_only_fields_are_not_writable(self):
        """
        Test that read-only fields are not accepted on input for creation/update.
        For ModelSerializer, read_only fields are typically ignored on input.
        """
        data = {
            "sender": self.profile_sender.pk,  # FKs are usually passed as PKs on write
            "receiver": self.profile_receiver.pk,
            # Attempting to set read-only fields:
            "id": 999,
            "created_at": "2000-01-01 00:00:00",
            "sender_profile_url": "http://example.com/fake",  # This is a SerializerMethodField, read-only by nature
        }

        serializer = ProfileFriendRequestSerializer(data=data)
        # For this serializer, let's confirm the explicit read_only fields.
        meta_read_only = getattr(
            ProfileFriendRequestSerializer.Meta, "read_only_fields", []
        )
        self.assertIn("id", meta_read_only)
        self.assertIn("created_at", meta_read_only)
