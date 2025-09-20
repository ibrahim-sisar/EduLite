# users/tests/models/test_user_profile_privacy_settings.py - Tests for UserProfilePrivacySettings model

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ...models import UserProfile, UserProfilePrivacySettings
from .. import UsersModelTestCase


class UserProfilePrivacySettingsModelTest(UsersModelTestCase):
    """Test cases for the UserProfilePrivacySettings model."""

    def test_privacy_settings_created_via_signal(self):
        """Test that privacy settings are created automatically with UserProfile."""
        user = self.create_test_user(username="privacytest")

        # Check that privacy settings exist
        self.assertTrue(hasattr(user.profile, "privacy_settings"))
        self.assertIsInstance(user.profile.privacy_settings, UserProfilePrivacySettings)

    def test_privacy_settings_defaults(self):
        """Test default values for privacy settings."""
        user = self.create_test_user(username="defaulttest")
        settings = user.profile.privacy_settings

        # Check defaults
        self.assertEqual(settings.search_visibility, "everyone")
        self.assertEqual(settings.profile_visibility, "friends_only")
        self.assertTrue(settings.show_full_name)
        self.assertFalse(settings.show_email)
        self.assertTrue(settings.allow_friend_requests)
        self.assertTrue(settings.allow_chat_invites)

    def test_privacy_settings_str_representation(self):
        """Test string representation of privacy settings."""
        user = self.create_test_user(username="strtest")
        settings = user.profile.privacy_settings

        expected = f"Privacy settings for {user.username}"
        self.assertEqual(str(settings), expected)

    def test_privacy_settings_validation_search_nobody_profile_public(self):
        """Test that profile cannot be public if search visibility is nobody."""
        user = self.create_test_user(username="validationtest")
        settings = user.profile.privacy_settings

        # This combination should raise ValidationError
        settings.search_visibility = "nobody"
        settings.profile_visibility = "public"

        with self.assertRaises(ValidationError) as context:
            settings.full_clean()

        self.assertIn(
            "Profile cannot be public if search visibility is set to nobody",
            str(context.exception),
        )

    def test_can_be_found_by_user_anonymous(self):
        """Test search visibility for anonymous users."""
        user = self.create_test_user(username="searchtest")
        settings = user.profile.privacy_settings

        # Test with 'everyone' visibility
        settings.search_visibility = "everyone"
        settings.save()
        self.assertTrue(settings.can_be_found_by_user(None))

        # Test with other visibility settings
        for visibility in ["friends_only", "friends_of_friends", "nobody"]:
            settings.search_visibility = visibility
            settings.save()
            self.assertFalse(settings.can_be_found_by_user(None))

    def test_can_be_found_by_user_self(self):
        """Test that users can always find themselves."""
        user = self.create_test_user(username="selftest")
        settings = user.profile.privacy_settings

        # Test all visibility settings - user should always find themselves
        for visibility in ["everyone", "friends_only", "friends_of_friends", "nobody"]:
            settings.search_visibility = visibility
            settings.save()
            self.assertTrue(settings.can_be_found_by_user(user))

    def test_can_be_found_by_user_everyone(self):
        """Test 'everyone' search visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        settings.search_visibility = "everyone"
        settings.save()

        self.assertTrue(settings.can_be_found_by_user(user2))

    def test_can_be_found_by_user_nobody(self):
        """Test 'nobody' search visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        settings.search_visibility = "nobody"
        settings.save()

        self.assertFalse(settings.can_be_found_by_user(user2))

    def test_can_be_found_by_user_friends_only(self):
        """Test 'friends_only' search visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        user3 = self.create_test_user(username="user3")
        settings = user1.profile.privacy_settings

        settings.search_visibility = "friends_only"
        settings.save()

        # Non-friend cannot find
        self.assertFalse(settings.can_be_found_by_user(user2))

        # Add as friend
        user1.profile.friends.add(user2)

        # Friend can find
        self.assertTrue(settings.can_be_found_by_user(user2))

        # Non-friend still cannot find
        self.assertFalse(settings.can_be_found_by_user(user3))

    def test_can_be_found_by_user_friends_of_friends(self):
        """Test 'friends_of_friends' search visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        user3 = self.create_test_user(username="user3")
        user4 = self.create_test_user(username="user4")
        settings = user1.profile.privacy_settings

        settings.search_visibility = "friends_of_friends"
        settings.save()

        # Direct friend can find
        user1.profile.friends.add(user2)
        self.assertTrue(settings.can_be_found_by_user(user2))

        # Friend of friend setup:
        # user1 is friends with user2
        # user2 is friends with user3
        # So user3 should be able to find user1 (through mutual friend user2)
        user2.profile.friends.add(user3)

        # Now user3 should be able to find user1 (through mutual friend user2)
        self.assertTrue(settings.can_be_found_by_user(user3))

        # User with no connection cannot find
        self.assertFalse(settings.can_be_found_by_user(user4))

    def test_can_profile_be_viewed_by_user_anonymous(self):
        """Test profile visibility for anonymous users."""
        user = self.create_test_user(username="profiletest")
        settings = user.profile.privacy_settings

        # Test with 'public' visibility
        settings.profile_visibility = "public"
        settings.save()
        self.assertTrue(settings.can_profile_be_viewed_by_user(None))

        # Test with other visibility settings
        for visibility in ["friends_only", "private"]:
            settings.profile_visibility = visibility
            settings.save()
            self.assertFalse(settings.can_profile_be_viewed_by_user(None))

    def test_can_profile_be_viewed_by_user_self(self):
        """Test that users can always view their own profile."""
        user = self.create_test_user(username="selfprofile")
        settings = user.profile.privacy_settings

        # Test all visibility settings
        for visibility in ["public", "friends_only", "private"]:
            settings.profile_visibility = visibility
            settings.save()
            self.assertTrue(settings.can_profile_be_viewed_by_user(user))

    def test_can_profile_be_viewed_by_user_public(self):
        """Test 'public' profile visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        settings.profile_visibility = "public"
        settings.save()

        self.assertTrue(settings.can_profile_be_viewed_by_user(user2))

    def test_can_profile_be_viewed_by_user_private(self):
        """Test 'private' profile visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        settings.profile_visibility = "private"
        settings.save()

        self.assertFalse(settings.can_profile_be_viewed_by_user(user2))

    def test_can_profile_be_viewed_by_user_friends_only(self):
        """Test 'friends_only' profile visibility."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        user3 = self.create_test_user(username="user3")
        settings = user1.profile.privacy_settings

        settings.profile_visibility = "friends_only"
        settings.save()

        # Non-friend cannot view
        self.assertFalse(settings.can_profile_be_viewed_by_user(user2))

        # Add as friend
        user1.profile.friends.add(user2)

        # Friend can view
        self.assertTrue(settings.can_profile_be_viewed_by_user(user2))

        # Non-friend still cannot view
        self.assertFalse(settings.can_profile_be_viewed_by_user(user3))

    def test_can_receive_friend_request_from_user_anonymous(self):
        """Test that anonymous users cannot send friend requests."""
        user = self.create_test_user(username="friendreqtest")
        settings = user.profile.privacy_settings

        self.assertFalse(settings.can_receive_friend_request_from_user(None))

    def test_can_receive_friend_request_from_user_self(self):
        """Test that users cannot send friend requests to themselves."""
        user = self.create_test_user(username="selfrequest")
        settings = user.profile.privacy_settings

        self.assertFalse(settings.can_receive_friend_request_from_user(user))

    def test_can_receive_friend_request_when_disabled(self):
        """Test friend request when allow_friend_requests is False."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        settings.allow_friend_requests = False
        settings.save()

        self.assertFalse(settings.can_receive_friend_request_from_user(user2))

    def test_can_receive_friend_request_from_existing_friend(self):
        """Test that existing friends cannot send friend requests."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        # Make them friends
        user1.profile.friends.add(user2)

        self.assertFalse(settings.can_receive_friend_request_from_user(user2))

    def test_can_receive_friend_request_valid(self):
        """Test valid friend request scenario."""
        user1 = self.create_test_user(username="user1")
        user2 = self.create_test_user(username="user2")
        settings = user1.profile.privacy_settings

        settings.allow_friend_requests = True
        settings.save()

        # Not friends, requests allowed - should return True
        self.assertTrue(settings.can_receive_friend_request_from_user(user2))

    def test_privacy_settings_cascade_delete(self):
        """Test that privacy settings are deleted when UserProfile is deleted."""
        user = self.create_test_user(username="deletetest")
        settings_id = user.profile.privacy_settings.id

        # Delete user (which cascades to profile and privacy settings)
        user.delete()

        # Check that privacy settings are deleted
        self.assertFalse(
            UserProfilePrivacySettings.objects.filter(id=settings_id).exists()
        )
