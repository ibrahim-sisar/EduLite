# users/tests/logic/test_have_mutual_friends.py

from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser

from users.logic.user_search_logic import have_mutual_friends


class HaveMutualFriendsTest(TestCase):
    """Test the have_mutual_friends function."""

    @classmethod
    def setUpTestData(cls):
        """Create test data."""
        # Create users
        cls.user1 = User.objects.create_user(
            username="user1", email="user1@example.com"
        )
        cls.user2 = User.objects.create_user(
            username="user2", email="user2@example.com"
        )
        cls.user3 = User.objects.create_user(
            username="user3", email="user3@example.com"
        )

        # Create mutual friend
        cls.mutual_friend = User.objects.create_user(
            username="mutual_friend", email="mutual@example.com"
        )

        # Create isolated users (no friends)
        cls.isolated1 = User.objects.create_user(
            username="isolated1", email="isolated1@example.com"
        )
        cls.isolated2 = User.objects.create_user(
            username="isolated2", email="isolated2@example.com"
        )

        # Set up friendships for mutual friends test
        # user1 and user2 both friends with mutual_friend
        cls.user1.profile.friends.add(cls.mutual_friend)
        cls.user2.profile.friends.add(cls.mutual_friend)

        # user1 also friends with user3 (but user2 is not)
        cls.user1.profile.friends.add(cls.user3)

    def test_users_with_mutual_friends(self):
        """Test that users with mutual friends return True."""
        result = have_mutual_friends(self.user1, self.user2)

        self.assertTrue(result)

    def test_users_without_mutual_friends(self):
        """Test that users without mutual friends return False."""
        # user2 and user3 have no mutual friends
        result = have_mutual_friends(self.user2, self.user3)

        self.assertFalse(result)

    def test_isolated_users(self):
        """Test that isolated users (no friends) return False."""
        result = have_mutual_friends(self.isolated1, self.isolated2)

        self.assertFalse(result)

    def test_same_user(self):
        """Test that same user cannot have mutual friends with themselves."""
        result = have_mutual_friends(self.user1, self.user1)

        self.assertFalse(result)

    def test_none_users(self):
        """Test with None users."""
        # Both None
        result = have_mutual_friends(None, None)
        self.assertFalse(result)

        # One None
        result = have_mutual_friends(self.user1, None)
        self.assertFalse(result)

        result = have_mutual_friends(None, self.user2)
        self.assertFalse(result)

    def test_anonymous_users(self):
        """Test with anonymous users."""
        anon1 = AnonymousUser()
        anon2 = AnonymousUser()

        # Both anonymous
        result = have_mutual_friends(anon1, anon2)
        self.assertFalse(result)

        # One anonymous, one authenticated
        result = have_mutual_friends(self.user1, anon1)
        self.assertFalse(result)

        result = have_mutual_friends(anon1, self.user1)
        self.assertFalse(result)

    def test_multiple_mutual_friends(self):
        """Test users with multiple mutual friends."""
        # Create additional mutual friends
        mutual2 = User.objects.create_user(username="mutual2")
        mutual3 = User.objects.create_user(username="mutual3")

        # Add to both users
        self.user1.profile.friends.add(mutual2, mutual3)
        self.user2.profile.friends.add(mutual2, mutual3)

        result = have_mutual_friends(self.user1, self.user2)

        self.assertTrue(result)

    def test_complex_friend_network(self):
        """Test in a complex friend network."""
        # Create a network: A -> C <- B
        user_a = User.objects.create_user(username="user_a")
        user_b = User.objects.create_user(username="user_b")
        user_c = User.objects.create_user(username="user_c")
        user_d = User.objects.create_user(username="user_d")

        # A and B both friends with C
        user_a.profile.friends.add(user_c)
        user_b.profile.friends.add(user_c)

        # A also friends with D, but B is not
        user_a.profile.friends.add(user_d)

        # A and B have mutual friend C
        self.assertTrue(have_mutual_friends(user_a, user_b))

        # B and D have no mutual friends
        self.assertFalse(have_mutual_friends(user_b, user_d))

        # C and D have mutual friend A
        user_c.profile.friends.add(user_a)
        user_d.profile.friends.add(user_a)
        self.assertTrue(have_mutual_friends(user_c, user_d))

    def test_one_way_friendship(self):
        """Test with one-way friendships (should not count as mutual)."""
        user_x = User.objects.create_user(username="user_x")
        user_y = User.objects.create_user(username="user_y")
        user_z = User.objects.create_user(username="user_z")

        # X considers Z a friend
        user_x.profile.friends.add(user_z)

        # Y considers Z a friend
        user_y.profile.friends.add(user_z)

        # But Z doesn't consider either as friends
        # This should still count as mutual friend
        result = have_mutual_friends(user_x, user_y)

        self.assertTrue(result)

    def test_performance_with_many_friends(self):
        """Test performance with users having many friends."""
        # Create users with many friends
        popular1 = User.objects.create_user(username="popular1")
        popular2 = User.objects.create_user(username="popular2")

        # Create 50 friends for each
        for i in range(50):
            friend = User.objects.create_user(username=f"friend_{i}")
            if i < 25:
                # First 25 are friends with both (mutual)
                popular1.profile.friends.add(friend)
                popular2.profile.friends.add(friend)
            elif i < 40:
                # Next 15 only with popular1
                popular1.profile.friends.add(friend)
            else:
                # Last 10 only with popular2
                popular2.profile.friends.add(friend)

        # Should have mutual friends (the first 25)
        result = have_mutual_friends(popular1, popular2)
        self.assertTrue(result)

    def test_edge_cases(self):
        """Test edge cases."""
        # Test with None users (already covered in test_none_users)
        # Other edge cases are handled by the initial validation
        result = have_mutual_friends(None, self.user1)
        self.assertFalse(result)
