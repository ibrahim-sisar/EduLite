# users/tests/logic/test_get_user_friends_ids.py

from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from users.logic.user_search_logic import get_user_friends_ids


class GetUserFriendsIdsTest(TestCase):
    """Test the get_user_friends_ids function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create main user
        cls.user = User.objects.create_user(
            username="main_user", email="main@example.com"
        )

        # Create friends
        cls.friend1 = User.objects.create_user(
            username="friend1", email="friend1@example.com"
        )
        cls.friend2 = User.objects.create_user(
            username="friend2", email="friend2@example.com"
        )
        cls.friend3 = User.objects.create_user(
            username="friend3", email="friend3@example.com"
        )

        # Create non-friend
        cls.non_friend = User.objects.create_user(
            username="non_friend", email="nonfriend@example.com"
        )

        # Set up friendships
        cls.user.profile.friends.add(cls.friend1, cls.friend2, cls.friend3)

        # Create user with no friends
        cls.lonely_user = User.objects.create_user(
            username="lonely_user", email="lonely@example.com"
        )

    def test_get_friends_ids_with_friends(self):
        """Test getting friend IDs for user with friends."""
        friend_ids = get_user_friends_ids(self.user)

        self.assertIsInstance(friend_ids, set)
        self.assertEqual(len(friend_ids), 3)
        self.assertIn(self.friend1.id, friend_ids)
        self.assertIn(self.friend2.id, friend_ids)
        self.assertIn(self.friend3.id, friend_ids)
        self.assertNotIn(self.non_friend.id, friend_ids)

    def test_get_friends_ids_no_friends(self):
        """Test getting friend IDs for user with no friends."""
        friend_ids = get_user_friends_ids(self.lonely_user)

        self.assertIsInstance(friend_ids, set)
        self.assertEqual(len(friend_ids), 0)

    def test_get_friends_ids_none_user(self):
        """Test with None user."""
        friend_ids = get_user_friends_ids(None)

        self.assertIsInstance(friend_ids, set)
        self.assertEqual(len(friend_ids), 0)

    def test_get_friends_ids_anonymous_user(self):
        """Test with anonymous user."""
        anon_user = AnonymousUser()
        friend_ids = get_user_friends_ids(anon_user)

        self.assertIsInstance(friend_ids, set)
        self.assertEqual(len(friend_ids), 0)

    def test_attribute_error_handling(self):
        """Test that AttributeError is handled gracefully."""

        # Create a mock user without proper profile
        class MockUser:
            def __init__(self):
                self.is_authenticated = True
                # No profile attribute

        mock_user = MockUser()
        friend_ids = get_user_friends_ids(mock_user)

        self.assertIsInstance(friend_ids, set)
        self.assertEqual(len(friend_ids), 0)

    def test_returns_user_ids_not_profile_ids(self):
        """Test that function returns user IDs, not profile IDs."""
        friend_ids = get_user_friends_ids(self.user)

        # Verify these are user IDs
        for friend_id in friend_ids:
            user = User.objects.get(id=friend_id)
            self.assertIn(user, [self.friend1, self.friend2, self.friend3])

    def test_friendship_is_based_on_profile(self):
        """Test that friendship is correctly read from profile."""
        # Add a friend through profile
        new_friend = User.objects.create_user(
            username="new_friend", email="new@example.com"
        )
        self.user.profile.friends.add(new_friend)

        friend_ids = get_user_friends_ids(self.user)

        self.assertIn(new_friend.id, friend_ids)
        self.assertEqual(len(friend_ids), 4)  # 3 original + 1 new

    def test_performance_with_many_friends(self):
        """Test performance with user having many friends."""
        # Create user with many friends
        popular_user = User.objects.create_user(
            username="popular", email="popular@example.com"
        )

        # Create 50 friends
        friends = []
        for i in range(50):
            friend = User.objects.create_user(
                username=f"friend_{i}", email=f"friend_{i}@example.com"
            )
            friends.append(friend)

        popular_user.profile.friends.add(*friends)

        # Should execute with single query
        with self.assertNumQueries(1):
            friend_ids = get_user_friends_ids(popular_user)

        self.assertEqual(len(friend_ids), 50)

    def test_empty_set_for_edge_cases(self):
        """Test that edge cases return empty set, not None or error."""
        test_cases = [
            None,
            AnonymousUser(),
        ]

        for test_case in test_cases:
            friend_ids = get_user_friends_ids(test_case)
            self.assertIsInstance(friend_ids, set)
            self.assertEqual(len(friend_ids), 0)
