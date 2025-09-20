# users/tests/logic/test_apply_privacy_filters.py

from django.test import TestCase
from django.contrib.auth.models import User

from users.logic.user_search_logic import apply_privacy_filters
from users.models import UserProfile, UserProfilePrivacySettings


class ApplyPrivacyFiltersTest(TestCase):
    """Test the apply_privacy_filters function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data with various privacy settings."""
        # Create users with different privacy settings

        # User 1: Everyone visibility
        cls.user_everyone = User.objects.create_user(
            username="user_everyone", first_name="Everyone", last_name="Visible"
        )
        cls.user_everyone.profile.privacy_settings.search_visibility = "everyone"
        cls.user_everyone.profile.privacy_settings.save()

        # User 2: Friends only visibility
        cls.user_friends_only = User.objects.create_user(
            username="user_friends_only", first_name="Friends", last_name="Only"
        )
        cls.user_friends_only.profile.privacy_settings.search_visibility = (
            "friends_only"
        )
        cls.user_friends_only.profile.privacy_settings.save()

        # User 3: Friends of friends visibility
        cls.user_friends_of_friends = User.objects.create_user(
            username="user_fof", first_name="Friends", last_name="Of Friends"
        )
        cls.user_friends_of_friends.profile.privacy_settings.search_visibility = (
            "friends_of_friends"
        )
        cls.user_friends_of_friends.profile.privacy_settings.save()

        # User 4: Nobody visibility
        cls.user_nobody = User.objects.create_user(
            username="user_nobody", first_name="Nobody", last_name="Visible"
        )
        cls.user_nobody.profile.privacy_settings.search_visibility = "nobody"
        cls.user_nobody.profile.privacy_settings.save()

        # Create a searcher user
        cls.searcher = User.objects.create_user(
            username="searcher", first_name="Search", last_name="User"
        )

        # Create mutual friend relationships
        cls.mutual_friend = User.objects.create_user(
            username="mutual_friend", first_name="Mutual", last_name="Friend"
        )

        # Set up friendships
        # searcher is friends with user_friends_only
        cls.searcher.profile.friends.add(cls.user_friends_only)
        cls.user_friends_only.profile.friends.add(cls.searcher)

        # searcher and user_friends_of_friends have a mutual friend
        cls.searcher.profile.friends.add(cls.mutual_friend)
        cls.mutual_friend.profile.friends.add(cls.searcher)
        cls.user_friends_of_friends.profile.friends.add(cls.mutual_friend)
        cls.mutual_friend.profile.friends.add(cls.user_friends_of_friends)

    def test_anonymous_user_sees_only_everyone(self):
        """Test that anonymous users can only see users with 'everyone' visibility."""
        # Get all users
        all_users = User.objects.all()

        # Apply privacy filters for anonymous user (None)
        filtered = apply_privacy_filters(all_users, None)

        # Should only see users with 'everyone' visibility
        for user in filtered:
            self.assertEqual(
                user.profile.privacy_settings.search_visibility,
                "everyone",
                f"Anonymous user should not see {user.username} with visibility {user.profile.privacy_settings.search_visibility}",
            )

        # Specific checks
        self.assertIn(self.user_everyone, filtered)
        self.assertNotIn(self.user_friends_only, filtered)
        self.assertNotIn(self.user_friends_of_friends, filtered)
        self.assertNotIn(self.user_nobody, filtered)

    def test_authenticated_user_sees_self(self):
        """Test that authenticated users can always see themselves."""
        # Get all users
        all_users = User.objects.all()

        # Apply privacy filters for searcher
        filtered = apply_privacy_filters(all_users, self.searcher)

        # Should see self regardless of privacy settings
        self.assertIn(self.searcher, filtered)

    def test_authenticated_user_sees_everyone_visibility(self):
        """Test that authenticated users can see 'everyone' visibility users."""
        all_users = User.objects.all()

        filtered = apply_privacy_filters(all_users, self.searcher)

        self.assertIn(self.user_everyone, filtered)

    def test_friends_only_visibility_with_friend(self):
        """Test that users can see 'friends_only' users they're friends with."""
        all_users = User.objects.all()

        filtered = apply_privacy_filters(all_users, self.searcher)

        # searcher is friends with user_friends_only
        self.assertIn(self.user_friends_only, filtered)

    def test_friends_only_visibility_without_friendship(self):
        """Test that users cannot see 'friends_only' users they're not friends with."""
        # Create a new user who is not friends with anyone
        non_friend = User.objects.create_user(username="non_friend")

        all_users = User.objects.all()
        filtered = apply_privacy_filters(all_users, non_friend)

        # Should not see user_friends_only
        self.assertNotIn(self.user_friends_only, filtered)

    def test_friends_of_friends_with_mutual_friend(self):
        """Test that users can see 'friends_of_friends' users with mutual friends."""
        all_users = User.objects.all()

        filtered = apply_privacy_filters(all_users, self.searcher)

        # searcher and user_friends_of_friends have mutual_friend in common
        self.assertIn(self.user_friends_of_friends, filtered)

    def test_friends_of_friends_with_direct_friendship(self):
        """Test that direct friends can see 'friends_of_friends' users."""
        # Make searcher direct friends with user_friends_of_friends
        self.searcher.profile.friends.add(self.user_friends_of_friends)
        self.user_friends_of_friends.profile.friends.add(self.searcher)

        all_users = User.objects.all()
        filtered = apply_privacy_filters(all_users, self.searcher)

        self.assertIn(self.user_friends_of_friends, filtered)

    def test_friends_of_friends_without_connection(self):
        """Test that users cannot see 'friends_of_friends' without any connection."""
        # Create isolated user
        isolated_user = User.objects.create_user(username="isolated")

        all_users = User.objects.all()
        filtered = apply_privacy_filters(all_users, isolated_user)

        self.assertNotIn(self.user_friends_of_friends, filtered)

    def test_nobody_visibility_never_shown(self):
        """Test that 'nobody' visibility users are never shown in search."""
        all_users = User.objects.all()

        # Test with various users
        filtered_anon = apply_privacy_filters(all_users, None)
        filtered_auth = apply_privacy_filters(all_users, self.searcher)

        self.assertNotIn(self.user_nobody, filtered_anon)
        self.assertNotIn(self.user_nobody, filtered_auth)

    def test_friend_id_caching(self):
        """Test that friend IDs are cached on the requesting user."""
        all_users = User.objects.all()

        # First call should cache friend IDs - force evaluation
        filtered = apply_privacy_filters(all_users, self.searcher)
        list(filtered)  # Force evaluation

        # Check that cache was set
        self.assertTrue(hasattr(self.searcher, "_prefetched_friend_ids"))
        self.assertIsInstance(self.searcher._prefetched_friend_ids, list)

        # Second call should use cached IDs - the caching logic is in the function,
        # but Django querysets are lazy, so we need to evaluate to see the effect
        filtered2 = apply_privacy_filters(all_users, self.searcher)
        # The cache should be used (verified by checking the attribute exists)
        self.assertTrue(hasattr(self.searcher, "_prefetched_friend_ids"))

    def test_complex_friend_network(self):
        """Test with a more complex friend network."""
        # Create a network: A -> B -> C -> D
        user_a = User.objects.create_user(username="user_a")
        user_b = User.objects.create_user(username="user_b")
        user_c = User.objects.create_user(username="user_c")
        user_d = User.objects.create_user(username="user_d")

        # Set visibility
        user_b.profile.privacy_settings.search_visibility = "friends_only"
        user_b.profile.privacy_settings.save()
        user_c.profile.privacy_settings.search_visibility = "friends_of_friends"
        user_c.profile.privacy_settings.save()
        user_d.profile.privacy_settings.search_visibility = "friends_of_friends"
        user_d.profile.privacy_settings.save()

        # Create friendships
        user_a.profile.friends.add(user_b)
        user_b.profile.friends.add(user_a, user_c)
        user_c.profile.friends.add(user_b, user_d)
        user_d.profile.friends.add(user_c)

        all_users = User.objects.all()
        filtered = apply_privacy_filters(all_users, user_a)

        # user_a should see:
        # - self (always)
        # - user_b (direct friend)
        # - user_c (friend of friend through user_b)
        # - NOT user_d (too far removed)
        self.assertIn(user_a, filtered)
        self.assertIn(user_b, filtered)
        self.assertIn(user_c, filtered)
        self.assertNotIn(user_d, filtered)

    def test_empty_queryset(self):
        """Test with empty queryset."""
        empty_qs = User.objects.none()

        filtered = apply_privacy_filters(empty_qs, self.searcher)

        self.assertEqual(filtered.count(), 0)
