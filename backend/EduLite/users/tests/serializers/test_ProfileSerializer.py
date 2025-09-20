# users/tests/serializers/test_ProfileSerializer.py - Tests for ProfileSerializer

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ...models import UserProfile, UserProfilePrivacySettings
from ...serializers import ProfileSerializer


class ProfileSerializerTest(TestCase):
    """Test cases for ProfileSerializer."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )

        # Get profile (created automatically via signal)
        self.profile = self.user.profile

        # Update profile with test data
        self.profile.bio = "Test bio for profile"
        self.profile.occupation = "Software Developer"
        self.profile.country = "US"
        self.profile.preferred_language = "en"
        self.profile.secondary_language = "es"
        self.profile.save()

        # Get privacy settings (created automatically via signal)
        self.privacy_settings = UserProfilePrivacySettings.objects.get(
            user_profile=self.profile
        )

        # Create request factory for context
        self.factory = APIRequestFactory()

    def get_serializer_context(self, user=None):
        """Get serializer context with request."""
        request = self.factory.get("/")
        if user:
            request.user = user
        else:
            # Create anonymous user for unauthenticated context
            from django.contrib.auth.models import AnonymousUser

            request.user = AnonymousUser()
        return {"request": request}

    # --- Field Presence Tests ---

    def test_serializer_contains_expected_fields_for_owner(self):
        """Test that serializer contains all expected fields for profile owner."""
        # Owner should see all fields
        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(self.user)
        )
        data = serializer.data

        expected_fields = [
            "url",
            "user",
            "user_url",
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_contains_limited_fields_for_strangers(self):
        """Test that serializer contains only limited fields for non-friends."""
        # Stranger should see only limited fields
        stranger = User.objects.create_user(username="stranger")
        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(stranger)
        )
        data = serializer.data

        # Should only have limited fields
        expected_limited_fields = ["url", "user_url"]

        for field in expected_limited_fields:
            self.assertIn(field, data)

        # Should not have private fields
        private_fields = ["bio", "occupation", "country", "friends"]
        for field in private_fields:
            self.assertNotIn(field, data)

    def test_serializer_contains_fields_for_friends(self):
        """Test that serializer contains all fields for friends."""
        # Create friend relationship
        friend = User.objects.create_user(username="friend")
        self.profile.friends.add(friend)

        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(friend)
        )
        data = serializer.data

        # Friends should see all fields
        expected_fields = [
            "url",
            "user",
            "user_url",
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_hyperlinked_fields_always_present(self):
        """Test that hyperlinked fields are always included even for strangers."""
        stranger = User.objects.create_user(username="stranger")
        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(stranger)
        )
        data = serializer.data

        # Check hyperlinked fields are present even for strangers
        self.assertIn("url", data)  # Profile URL
        self.assertIn("user_url", data)  # User URL

        # Should be strings (URLs) if context provided
        if data["url"]:
            self.assertIsInstance(data["url"], str)
        if data["user_url"]:
            self.assertIsInstance(data["user_url"], str)

    # --- Field Value Tests ---

    def test_basic_field_values_for_owner(self):
        """Test basic field values are correct for profile owner."""
        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(self.user)
        )
        data = serializer.data

        # Check field values - owner should see all data
        self.assertEqual(data["user"], self.user.id)
        self.assertEqual(data["bio"], "Test bio for profile")
        self.assertEqual(data["occupation"], "Software Developer")
        self.assertEqual(data["country"], "US")
        self.assertEqual(data["preferred_language"], "en")
        self.assertEqual(data["secondary_language"], "es")

    def test_friends_field_for_owner(self):
        """Test friends field returns user list for profile owner."""
        # Add some friends
        friend1 = User.objects.create_user(username="friend1")
        friend2 = User.objects.create_user(username="friend2")
        self.profile.friends.add(friend1, friend2)

        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(self.user)
        )
        data = serializer.data

        # Friends should be a list for owner
        self.assertIn("friends", data)
        self.assertIsInstance(data["friends"], list)
        self.assertEqual(len(data["friends"]), 2)

    def test_friends_field_hidden_for_strangers(self):
        """Test friends field is hidden for strangers."""
        # Add some friends
        friend1 = User.objects.create_user(username="friend1")
        friend2 = User.objects.create_user(username="friend2")
        self.profile.friends.add(friend1, friend2)

        stranger = User.objects.create_user(username="stranger")
        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(stranger)
        )
        data = serializer.data

        # Friends should not be visible to strangers
        self.assertNotIn("friends", data)

    def test_empty_optional_fields_for_owner(self):
        """Test handling of empty optional fields for profile owner."""
        # Create user with minimal data (profile created automatically)
        minimal_user = User.objects.create_user(username="minimal_user")
        minimal_profile = minimal_user.profile

        serializer = ProfileSerializer(
            instance=minimal_profile, context=self.get_serializer_context(minimal_user)
        )
        data = serializer.data

        # Optional fields should be present for owner but may be None/empty
        self.assertIn("bio", data)
        self.assertIn("occupation", data)
        self.assertIn("website_url", data)
        # Values might be None or empty string depending on model defaults
        self.assertIn(data["bio"], ["", None])
        self.assertIn(data["occupation"], ["", None])
        self.assertIn(data["website_url"], ["", None])

    # --- Privacy Tests ---

    def test_admin_can_see_all_fields(self):
        """Test that admin users can see all profile fields."""
        admin_user = User.objects.create_user(username="admin", is_staff=True)

        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(admin_user)
        )
        data = serializer.data

        # Admin should see all fields
        expected_fields = [
            "url",
            "user",
            "user_url",
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_superuser_can_see_all_fields(self):
        """Test that superusers can see all profile fields."""
        superuser = User.objects.create_user(username="superuser", is_superuser=True)

        serializer = ProfileSerializer(
            instance=self.profile, context=self.get_serializer_context(superuser)
        )
        data = serializer.data

        # Superuser should see all fields
        expected_fields = [
            "url",
            "user",
            "user_url",
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    # --- Serialization Tests ---

    def test_serialize_multiple_profiles_as_admin(self):
        """Test serializing multiple profiles as admin."""
        # Create additional user (profile created automatically)
        user2 = User.objects.create_user(username="user2")
        profile2 = user2.profile
        profile2.bio = "Second profile bio"
        profile2.save()

        admin_user = User.objects.create_user(username="admin", is_staff=True)

        profiles = UserProfile.objects.filter(user__in=[self.user, user2])
        serializer = ProfileSerializer(
            profiles, many=True, context=self.get_serializer_context(admin_user)
        )
        data = serializer.data

        self.assertEqual(len(data), 2)
        # Admin should see bios in all profiles
        bios = [profile.get("bio", "") for profile in data]
        self.assertIn("Test bio for profile", bios)
        self.assertIn("Second profile bio", bios)

    def test_serialize_multiple_profiles_as_stranger(self):
        """Test serializing multiple profiles as stranger shows limited data."""
        # Create additional user (profile created automatically)
        user2 = User.objects.create_user(username="user2")
        profile2 = user2.profile
        profile2.bio = "Second profile bio"
        profile2.save()

        stranger = User.objects.create_user(username="stranger")

        profiles = UserProfile.objects.filter(user__in=[self.user, user2])
        serializer = ProfileSerializer(
            profiles, many=True, context=self.get_serializer_context(stranger)
        )
        data = serializer.data

        self.assertEqual(len(data), 2)
        # Stranger should not see bios
        for profile_data in data:
            self.assertNotIn("bio", profile_data)
            # Should only have limited fields
            self.assertIn("url", profile_data)
            self.assertIn("user_url", profile_data)

    def test_read_only_fields(self):
        """Test that read-only fields cannot be written."""
        # user and user_url are read-only
        data = {
            "bio": "Updated bio",
            "user": 999,  # Should be ignored
            "user_url": "http://fake.com/user/999/",  # Should be ignored
        }

        serializer = ProfileSerializer(
            instance=self.profile,
            data=data,
            partial=True,
            context=self.get_serializer_context(self.user),
        )

        self.assertTrue(serializer.is_valid())

        # The read-only fields should not be in validated_data
        self.assertNotIn("user", serializer.validated_data)
        self.assertNotIn("user_url", serializer.validated_data)

        # But bio should be there
        self.assertIn("bio", serializer.validated_data)
        self.assertEqual(serializer.validated_data["bio"], "Updated bio")

    # --- Test Context Variations ---

    def test_serializer_with_test_user_context(self):
        """Test that serializer works with test_user context for testing."""
        # Test the test_user context feature - need request for HyperlinkedModelSerializer
        request = self.factory.get("/")
        context = {"request": request, "test_user": self.user}
        serializer = ProfileSerializer(instance=self.profile, context=context)
        data = serializer.data

        # Should see all fields with test_user context
        expected_fields = [
            "url",
            "user",
            "user_url",
            "bio",
            "occupation",
            "country",
            "preferred_language",
            "secondary_language",
            "picture",
            "website_url",
            "friends",
        ]

        for field in expected_fields:
            self.assertIn(field, data)

    def test_serializer_without_authenticated_user(self):
        """Test serializer behavior with anonymous user."""
        # Use anonymous user context instead of no context
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/")
        request.user = AnonymousUser()
        context = {"request": request}

        serializer = ProfileSerializer(instance=self.profile, context=context)
        data = serializer.data

        # Anonymous user should show only limited fields
        expected_limited_fields = ["url", "user_url"]

        for field in expected_limited_fields:
            self.assertIn(field, data)

        # Should not have private fields
        private_fields = ["bio", "occupation", "country", "friends"]
        for field in private_fields:
            self.assertNotIn(field, data)
