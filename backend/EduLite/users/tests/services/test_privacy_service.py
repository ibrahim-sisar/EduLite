"""
Tests for PrivacyService - centralized privacy and visibility logic.

These tests verify that all privacy rules work correctly when consolidated
in the PrivacyService class.
"""

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from users.models import ProfileFriendRequest, UserProfile
from users.services import PrivacyService


class PrivacyServiceTestCase(TestCase):
    """Base test case with common setup for privacy service tests."""

    def setUp(self):
        """Set up test users with profiles and privacy settings."""
        # Create test users (profiles created automatically via signals)
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            first_name="User",
            last_name="One",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            first_name="User",
            last_name="Two",
        )
        self.user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            first_name="User",
            last_name="Three",
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            is_staff=True,
            is_superuser=True,
        )

        # Get profiles and privacy settings
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.profile3 = self.user3.profile
        self.privacy1 = self.profile1.privacy_settings
        self.privacy2 = self.profile2.privacy_settings

        # Anonymous user for testing
        self.anonymous = AnonymousUser()


class CanBeFoundByUserTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.can_be_found_by_user()"""

    def test_everyone_visibility_anonymous_user(self):
        """Anonymous users can find profiles with 'everyone' visibility."""
        self.privacy1.search_visibility = "everyone"
        self.privacy1.save()

        result = PrivacyService.can_be_found_by_user(self.privacy1, None)
        self.assertTrue(result)

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.anonymous)
        self.assertTrue(result)

    def test_everyone_visibility_authenticated_user(self):
        """Authenticated users can find profiles with 'everyone' visibility."""
        self.privacy1.search_visibility = "everyone"
        self.privacy1.save()

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertTrue(result)

    def test_nobody_visibility_anonymous_user(self):
        """Anonymous users cannot find profiles with 'nobody' visibility."""
        self.privacy1.search_visibility = "nobody"
        self.privacy1.profile_visibility = "private"  # Required for validation
        self.privacy1.save()

        result = PrivacyService.can_be_found_by_user(self.privacy1, None)
        self.assertFalse(result)

    def test_nobody_visibility_authenticated_user(self):
        """Authenticated users cannot find profiles with 'nobody' visibility."""
        self.privacy1.search_visibility = "nobody"
        self.privacy1.profile_visibility = "private"
        self.privacy1.save()

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_user_can_always_find_themselves(self):
        """Users can always find themselves regardless of visibility settings."""
        self.privacy1.search_visibility = "nobody"
        self.privacy1.profile_visibility = "private"
        self.privacy1.save()

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user1)
        self.assertTrue(result)

    def test_friends_only_visibility_non_friend(self):
        """Non-friends cannot find profiles with 'friends_only' visibility."""
        self.privacy1.search_visibility = "friends_only"
        self.privacy1.save()

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_friends_only_visibility_friend(self):
        """Friends can find profiles with 'friends_only' visibility."""
        self.privacy1.search_visibility = "friends_only"
        self.privacy1.save()

        # Make them friends
        self.profile1.friends.add(self.user2)

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertTrue(result)

    def test_friends_of_friends_visibility_direct_friend(self):
        """Direct friends can find profiles with 'friends_of_friends' visibility."""
        self.privacy1.search_visibility = "friends_of_friends"
        self.privacy1.save()

        # Make them direct friends
        self.profile1.friends.add(self.user2)

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertTrue(result)

    def test_friends_of_friends_visibility_mutual_friend(self):
        """Users with mutual friends can find profiles with 'friends_of_friends' visibility."""
        self.privacy1.search_visibility = "friends_of_friends"
        self.privacy1.save()

        # user1 is friends with user3, user3 is friends with user2
        # So user2 should be able to find user1 (mutual friend: user3)
        self.profile1.friends.add(self.user3)
        self.profile3.friends.add(self.user2)

        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertTrue(result)

    def test_friends_of_friends_visibility_no_mutual_friends(self):
        """Users without mutual friends cannot find 'friends_of_friends' profiles."""
        self.privacy1.search_visibility = "friends_of_friends"
        self.privacy1.save()

        # No friendship connections
        result = PrivacyService.can_be_found_by_user(self.privacy1, self.user2)
        self.assertFalse(result)


class CanViewFullProfileTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.can_view_full_profile()"""

    def test_public_visibility_anonymous_user(self):
        """Anonymous users can view public profiles."""
        self.privacy1.profile_visibility = "public"
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, None)
        self.assertTrue(result)

    def test_public_visibility_authenticated_user(self):
        """Authenticated users can view public profiles."""
        self.privacy1.profile_visibility = "public"
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, self.user2)
        self.assertTrue(result)

    def test_private_visibility_anonymous_user(self):
        """Anonymous users cannot view private profiles."""
        self.privacy1.profile_visibility = "private"
        self.privacy1.search_visibility = "nobody"  # Required for validation
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, None)
        self.assertFalse(result)

    def test_private_visibility_authenticated_user(self):
        """Authenticated users cannot view private profiles."""
        self.privacy1.profile_visibility = "private"
        self.privacy1.search_visibility = "nobody"
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_user_can_always_view_own_profile(self):
        """Users can always view their own profile."""
        self.privacy1.profile_visibility = "private"
        self.privacy1.search_visibility = "nobody"
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, self.user1)
        self.assertTrue(result)

    def test_admin_can_view_any_profile(self):
        """Admin/staff users can view any profile."""
        self.privacy1.profile_visibility = "private"
        self.privacy1.search_visibility = "nobody"
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, self.admin_user)
        self.assertTrue(result)

    def test_friends_only_visibility_non_friend(self):
        """Non-friends cannot view 'friends_only' profiles."""
        self.privacy1.profile_visibility = "friends_only"
        self.privacy1.save()

        result = PrivacyService.can_view_full_profile(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_friends_only_visibility_friend(self):
        """Friends can view 'friends_only' profiles."""
        self.privacy1.profile_visibility = "friends_only"
        self.privacy1.save()

        # Make them friends
        self.profile1.friends.add(self.user2)

        result = PrivacyService.can_view_full_profile(self.privacy1, self.user2)
        self.assertTrue(result)


class CanReceiveFriendRequestTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.can_receive_friend_request()"""

    def test_anonymous_user_cannot_send_request(self):
        """Anonymous users cannot send friend requests."""
        result = PrivacyService.can_receive_friend_request(self.privacy1, None)
        self.assertFalse(result)

        result = PrivacyService.can_receive_friend_request(
            self.privacy1, self.anonymous
        )
        self.assertFalse(result)

    def test_user_cannot_send_request_to_self(self):
        """Users cannot send friend requests to themselves."""
        result = PrivacyService.can_receive_friend_request(self.privacy1, self.user1)
        self.assertFalse(result)

    def test_friend_requests_disabled(self):
        """Cannot send request when friend requests are disabled."""
        self.privacy1.allow_friend_requests = False
        self.privacy1.save()

        result = PrivacyService.can_receive_friend_request(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_already_friends(self):
        """Cannot send request when already friends."""
        self.profile1.friends.add(self.user2)

        result = PrivacyService.can_receive_friend_request(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_pending_request_exists(self):
        """Cannot send request when pending request already exists."""
        # Create existing pending request
        ProfileFriendRequest.objects.create(
            sender=self.profile2,
            receiver=self.profile1,
        )

        result = PrivacyService.can_receive_friend_request(self.privacy1, self.user2)
        self.assertFalse(result)

    def test_can_send_request_when_allowed(self):
        """Can send request when all conditions are met."""
        self.privacy1.allow_friend_requests = True
        self.privacy1.save()

        result = PrivacyService.can_receive_friend_request(self.privacy1, self.user2)
        self.assertTrue(result)


class ShouldShowEmailTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.should_show_email()"""

    def test_user_can_see_own_email(self):
        """Users can always see their own email."""
        self.privacy1.show_email = False
        self.privacy1.save()

        result = PrivacyService.should_show_email(self.user1, self.user1)
        self.assertTrue(result)

    def test_admin_can_see_any_email(self):
        """Admin users can see any email."""
        self.privacy1.show_email = False
        self.privacy1.save()

        result = PrivacyService.should_show_email(self.user1, self.admin_user)
        self.assertTrue(result)

    def test_show_email_enabled(self):
        """Email is shown when show_email is True."""
        self.privacy1.show_email = True
        self.privacy1.save()

        result = PrivacyService.should_show_email(self.user1, self.user2)
        self.assertTrue(result)

    def test_show_email_disabled(self):
        """Email is hidden when show_email is False."""
        self.privacy1.show_email = False
        self.privacy1.save()

        result = PrivacyService.should_show_email(self.user1, self.user2)
        self.assertFalse(result)

    def test_anonymous_user_default_hidden(self):
        """Email is hidden from anonymous users by default."""
        self.privacy1.show_email = False
        self.privacy1.save()

        result = PrivacyService.should_show_email(self.user1, None)
        self.assertFalse(result)


class ShouldShowFullNameTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.should_show_full_name()"""

    def test_user_can_see_own_name(self):
        """Users can always see their own name."""
        self.privacy1.show_full_name = False
        self.privacy1.save()

        result = PrivacyService.should_show_full_name(self.user1, self.user1)
        self.assertTrue(result)

    def test_admin_can_see_any_name(self):
        """Admin users can see any name."""
        self.privacy1.show_full_name = False
        self.privacy1.save()

        result = PrivacyService.should_show_full_name(self.user1, self.admin_user)
        self.assertTrue(result)

    def test_show_full_name_enabled(self):
        """Name is shown when show_full_name is True."""
        self.privacy1.show_full_name = True
        self.privacy1.save()

        result = PrivacyService.should_show_full_name(self.user1, self.user2)
        self.assertTrue(result)

    def test_show_full_name_disabled(self):
        """Name is hidden when show_full_name is False."""
        self.privacy1.show_full_name = False
        self.privacy1.save()

        result = PrivacyService.should_show_full_name(self.user1, self.user2)
        self.assertFalse(result)

    def test_default_shows_name(self):
        """Name is shown by default (show_full_name defaults to True)."""
        # Default value should be True
        result = PrivacyService.should_show_full_name(self.user1, self.user2)
        self.assertTrue(result)


class GetVisibleFieldsTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.get_visible_fields()"""

    def test_base_fields_always_visible(self):
        """Base fields (url, username, profile_url) are always visible."""
        result = PrivacyService.get_visible_fields(self.user1, self.user2)

        self.assertIn("url", result)
        self.assertIn("username", result)
        self.assertIn("profile_url", result)

    def test_email_visible_when_allowed(self):
        """Email field is included when show_email is True."""
        self.privacy1.show_email = True
        self.privacy1.save()

        result = PrivacyService.get_visible_fields(self.user1, self.user2)
        self.assertIn("email", result)

    def test_email_hidden_when_not_allowed(self):
        """Email field is excluded when show_email is False."""
        self.privacy1.show_email = False
        self.privacy1.save()

        result = PrivacyService.get_visible_fields(self.user1, self.user2)
        self.assertNotIn("email", result)

    def test_name_fields_visible_when_allowed(self):
        """Name fields are included when show_full_name is True."""
        self.privacy1.show_full_name = True
        self.privacy1.save()

        result = PrivacyService.get_visible_fields(self.user1, self.user2)
        self.assertIn("first_name", result)
        self.assertIn("last_name", result)
        self.assertIn("full_name", result)

    def test_name_fields_hidden_when_not_allowed(self):
        """Name fields are excluded when show_full_name is False."""
        self.privacy1.show_full_name = False
        self.privacy1.save()

        result = PrivacyService.get_visible_fields(self.user1, self.user2)
        self.assertNotIn("first_name", result)
        self.assertNotIn("last_name", result)
        self.assertNotIn("full_name", result)


class HaveMutualFriendsTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.have_mutual_friends()"""

    def test_no_mutual_friends(self):
        """Returns False when users have no mutual friends."""
        result = PrivacyService.have_mutual_friends(self.profile1, self.user2)
        self.assertFalse(result)

    def test_has_mutual_friend(self):
        """Returns True when users have a mutual friend."""
        # user1 is friends with user3
        self.profile1.friends.add(self.user3)
        # user3 is friends with user2
        self.profile3.friends.add(self.user2)

        result = PrivacyService.have_mutual_friends(self.profile1, self.user2)
        self.assertTrue(result)

    def test_direct_friends_not_mutual(self):
        """Direct friendship doesn't count as mutual friends."""
        # user1 and user2 are direct friends, but no third party
        self.profile1.friends.add(self.user2)

        # This should be False because there's no mutual friend (third party)
        # The method checks if user1's friends have user2 as a friend
        result = PrivacyService.have_mutual_friends(self.profile1, self.user2)
        # Actually, this will check if any of user1's friends (user2)
        # have user2 as a friend in their profile. user2's profile.friends
        # doesn't include user2, so this should be False.
        self.assertFalse(result)


class GetUserFriendsIdsTests(PrivacyServiceTestCase):
    """Tests for PrivacyService.get_user_friends_ids()"""

    def test_no_friends(self):
        """Returns empty set when user has no friends."""
        result = PrivacyService.get_user_friends_ids(self.user1)
        self.assertEqual(result, set())

    def test_has_friends(self):
        """Returns set of friend IDs."""
        self.profile1.friends.add(self.user2)
        self.profile1.friends.add(self.user3)

        result = PrivacyService.get_user_friends_ids(self.user1)
        self.assertEqual(result, {self.user2.id, self.user3.id})

    def test_anonymous_user(self):
        """Returns empty set for anonymous users."""
        result = PrivacyService.get_user_friends_ids(self.anonymous)
        self.assertEqual(result, set())

    def test_none_user(self):
        """Returns empty set for None user."""
        result = PrivacyService.get_user_friends_ids(None)
        self.assertEqual(result, set())
