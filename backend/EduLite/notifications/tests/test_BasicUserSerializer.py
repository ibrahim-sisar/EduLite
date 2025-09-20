# backend/EduLite/notifications/tests/test_BasicUserSerializer.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from notifications.serializers import BasicUserSerializer

User = get_user_model()


class BasicUserSerializerTests(TestCase):
    """
    Test suite for the BasicUserSerializer.
    This serializer provides lightweight user representation for notifications.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up non-modified objects used by all test methods.
        This is run once for the entire class.
        """
        cls.user_with_full_name = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
        )

        cls.user_minimal = User.objects.create_user(
            username="minimaluser",
            email="minimal@example.com",
            password="password123",
            # No first_name or last_name
        )

    def test_serializer_contains_expected_fields(self):
        """
        Test that the serializer output contains all expected fields.
        """
        serializer = BasicUserSerializer(self.user_with_full_name)
        data = serializer.data
        expected_keys = ["id", "username", "first_name", "last_name"]
        self.assertEqual(set(data.keys()), set(expected_keys))

    def test_serializer_with_full_name(self):
        """
        Test serialization of user with complete name information.
        """
        serializer = BasicUserSerializer(self.user_with_full_name)
        data = serializer.data

        self.assertEqual(data["id"], self.user_with_full_name.id)
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["first_name"], "John")
        self.assertEqual(data["last_name"], "Doe")

    def test_serializer_with_minimal_user(self):
        """
        Test serialization of user with minimal information (no names).
        """
        serializer = BasicUserSerializer(self.user_minimal)
        data = serializer.data

        self.assertEqual(data["id"], self.user_minimal.id)
        self.assertEqual(data["username"], "minimaluser")
        self.assertEqual(data["first_name"], "")
        self.assertEqual(data["last_name"], "")

    def test_all_fields_are_read_only(self):
        """
        Test that all fields are read-only and cannot be used for updates.
        """
        # Get the serializer's Meta class read_only_fields
        meta_read_only = getattr(BasicUserSerializer.Meta, "read_only_fields", [])
        expected_read_only = ["id", "username", "first_name", "last_name"]

        for field in expected_read_only:
            self.assertIn(
                field, meta_read_only, f"Field '{field}' should be in read_only_fields"
            )

    def test_serializer_does_not_expose_sensitive_data(self):
        """
        Test that the serializer doesn't expose sensitive user data.
        """
        serializer = BasicUserSerializer(self.user_with_full_name)
        data = serializer.data

        # Ensure sensitive fields are not present
        sensitive_fields = ["password", "email", "is_superuser", "is_staff", "groups"]
        for field in sensitive_fields:
            self.assertNotIn(
                field,
                data.keys(),
                f"Sensitive field '{field}' should not be in serialized data",
            )

    def test_multiple_users_serialization(self):
        """
        Test serialization of multiple users (many=True).
        """
        users = [self.user_with_full_name, self.user_minimal]
        serializer = BasicUserSerializer(users, many=True)
        data = serializer.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["username"], "testuser")
        self.assertEqual(data[1]["username"], "minimaluser")

    def test_serializer_with_none_user(self):
        """
        Test serializer behavior when user is None.
        """
        serializer = BasicUserSerializer(None)
        data = serializer.data

        # When serializing None, DRF typically returns None or empty dict
        # The exact behavior depends on how it's used in context
        self.assertEqual(data, {})
