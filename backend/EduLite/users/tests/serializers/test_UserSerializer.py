# users/tests/serializers/test_UserSerializer.py - Tests for UserSerializer

from django.contrib.auth.models import User, Group
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ...models import UserProfile, UserProfilePrivacySettings
from ...serializers import UserSerializer


class UserSerializerTest(TestCase):
    """Test cases for UserSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )

        # Get profile and privacy settings (created automatically via signals)
        self.profile = self.user.profile
        self.privacy_settings = self.profile.privacy_settings

        # Create request factory for context
        self.factory = APIRequestFactory()

        # Create test group
        self.test_group = Group.objects.create(name="TestGroup")
        self.user.groups.add(self.test_group)

    def get_serializer_context(self, user=None):
        """Get serializer context with request."""
        request = self.factory.get("/")
        if user:
            request.user = user
        return {"request": request}

    # --- Field Presence Tests ---

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        # Set privacy to show email
        self.privacy_settings.show_email = True
        self.privacy_settings.save()

        serializer = UserSerializer(
            instance=self.user,
            context=self.get_serializer_context(
                user=self.user
            ),  # User viewing own profile
        )
        data = serializer.data

        expected_fields = [
            "id",
            "url",
            "profile_url",
            "username",
            "email",
            "groups",
            "first_name",
            "last_name",
            "full_name",
        ]
        for field in expected_fields:
            self.assertIn(field, data)

    def test_hyperlinked_fields_present(self):
        """Test that hyperlinked fields are properly included."""
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context()
        )
        data = serializer.data

        # Check URL fields
        self.assertIn("url", data)
        self.assertIn("profile_url", data)

        # URL fields should be strings (URLs)
        if data["url"]:
            self.assertIsInstance(data["url"], str)
        if data["profile_url"]:
            self.assertIsInstance(data["profile_url"], str)

    # --- Field Value Tests ---

    def test_basic_field_values(self):
        """Test basic field values are correct."""
        # Set privacy to show email
        self.privacy_settings.show_email = True
        self.privacy_settings.save()

        serializer = UserSerializer(
            instance=self.user,
            context=self.get_serializer_context(
                user=self.user
            ),  # User viewing own profile
        )
        data = serializer.data

        self.assertEqual(data["id"], self.user.id)
        self.assertEqual(data["username"], "test_user")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")

    def test_full_name_computed_field(self):
        """Test full_name SerializerMethodField."""
        # Test with both first and last name
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context()
        )
        self.assertEqual(serializer.data["full_name"], "Test User")

        # Test with only first name
        self.user.last_name = ""
        self.user.save()
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context()
        )
        self.assertEqual(serializer.data["full_name"], "Test")

        # Test with only last name
        self.user.first_name = ""
        self.user.last_name = "User"
        self.user.save()
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context()
        )
        self.assertEqual(serializer.data["full_name"], "User")

        # Test with no names
        self.user.first_name = ""
        self.user.last_name = ""
        self.user.save()
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context()
        )
        self.assertEqual(serializer.data["full_name"], "")

    def test_groups_field(self):
        """Test groups field contains user's groups."""
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context()
        )
        data = serializer.data

        # Groups should be a list
        self.assertIsInstance(data["groups"], list)
        self.assertEqual(len(data["groups"]), 1)

    # --- Privacy Tests ---

    def test_email_hidden_based_on_privacy_settings(self):
        """Test that email is hidden when privacy settings dictate."""
        # Set privacy to hide email
        self.privacy_settings.show_email = False
        self.privacy_settings.save()

        # Another user viewing
        other_user = User.objects.create_user(username="other_user")

        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context(user=other_user)
        )
        data = serializer.data

        # Email should be hidden
        self.assertNotIn("email", data)

    def test_email_visible_to_self(self):
        """Test that email is always visible to the user themselves."""
        # Set privacy to hide email
        self.privacy_settings.show_email = False
        self.privacy_settings.save()

        # User viewing their own profile
        serializer = UserSerializer(
            instance=self.user, context=self.get_serializer_context(user=self.user)
        )
        data = serializer.data

        # Email should be visible
        self.assertIn("email", data)
        self.assertEqual(data["email"], "test@example.com")

    # --- Serializer Context Tests ---

    def test_serializer_requires_request_context_for_hyperlinks(self):
        """Test serializer requires request context for hyperlinked fields."""
        # Without context, hyperlinked fields should raise error
        serializer = UserSerializer(instance=self.user)

        # Accessing data should raise AssertionError due to missing context
        with self.assertRaises(AssertionError) as cm:
            data = serializer.data

        self.assertIn("request", str(cm.exception))

    def test_serialize_multiple_users(self):
        """Test serializing multiple users."""
        # Create additional user (profile created automatically)
        user2 = User.objects.create_user(
            username="user2", first_name="Second", last_name="User"
        )

        users = User.objects.all()
        serializer = UserSerializer(
            users, many=True, context=self.get_serializer_context()
        )
        data = serializer.data

        self.assertEqual(len(data), 2)
        usernames = [user["username"] for user in data]
        self.assertIn("test_user", usernames)
        self.assertIn("user2", usernames)
