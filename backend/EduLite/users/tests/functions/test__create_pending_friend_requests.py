# users/tests/functions/test__create_pending_friend_requests.py

import random

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import models, IntegrityError, transaction

from unittest.mock import patch

# Import the function to be tested and necessary models
# Adjust the import path based on your file structure
from ...management.logic import _create_pending_friend_requests
from ...models import UserProfile, ProfileFriendRequest

User = get_user_model()

# Define the full path to the logic module for patching
LOGIC_MODULE_PATH = 'users.management.logic'

class CreatePendingFriendRequestsTests(TestCase):
    """
    Test suite for the _create_pending_friend_requests helper function.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users and their profiles
        cls.user1 = User.objects.create_user(username='user1', password='password123')
        cls.profile1 = UserProfile.objects.get(user=cls.user1)

        cls.user2 = User.objects.create_user(username='user2', password='password123')
        cls.profile2 = UserProfile.objects.get(user=cls.user2)

        cls.user3 = User.objects.create_user(username='user3', password='password123')
        cls.profile3 = UserProfile.objects.get(user=cls.user3)

        cls.all_users = [cls.user1, cls.user2, cls.user3]

    def test_creates_no_requests_for_small_list(self):
        """
        Test that the function handles lists with 0 or 1 user gracefully.
        """
        # Test with an empty list
        result_empty = _create_pending_friend_requests([])
        self.assertEqual(len(result_empty), 0)
        self.assertEqual(ProfileFriendRequest.objects.count(), 0)

        # Test with a single user
        result_single = _create_pending_friend_requests([self.user1])
        self.assertEqual(len(result_single), 0)
        self.assertEqual(ProfileFriendRequest.objects.count(), 0)

    @patch(f'{LOGIC_MODULE_PATH}.random.sample')
    @patch(f'{LOGIC_MODULE_PATH}.random.randint')
    def test_creates_requests_successfully(self, mock_randint, mock_sample):
        """
        Test the successful creation of friend requests under controlled "random" conditions.
        """
        # --- Setup Mocks ---
        # Force each user to try and send exactly 1 request
        mock_randint.return_value = 1
        # Force user1 to send to user2, user2 to user3, and user3 to user1
        mock_sample.side_effect = [
            [self.user2],  # When sender is user1, sample returns user2
            [self.user3],  # When sender is user2, sample returns user3
            [self.user1],  # When sender is user3, sample returns user1
        ]
        
        # --- Action ---
        created_requests = _create_pending_friend_requests(self.all_users)

        # --- Assertions ---
        self.assertEqual(len(created_requests), 3)
        self.assertEqual(ProfileFriendRequest.objects.count(), 3)
        # Check one of the created requests for correctness
        self.assertTrue(ProfileFriendRequest.objects.filter(sender=self.profile1, receiver=self.profile2).exists())
        
    @patch(f'{LOGIC_MODULE_PATH}.random.sample')
    @patch(f'{LOGIC_MODULE_PATH}.random.randint')
    def test_skips_creating_request_if_already_friends(self, mock_randint, mock_sample):
        """
        Test that no friend request is created between users who are already friends.
        """
        # --- Setup ---
        # Make user1 and user2 friends before running the function
        self.profile1.friends.add(self.user2)
        
        # --- Setup Mocks ---
        # Force each user to try and send 1 request
        mock_randint.return_value = 1
        # Force user1 to attempt to send a request to user2 (who is already a friend)
        mock_sample.side_effect = [
            [self.user2],  # user1 -> user2
            [self.user1],  # user2 -> user1
            [self.user1],  # user3 -> user1
        ]

        # --- Action ---
        _create_pending_friend_requests(self.all_users)
        
        # --- Assertions ---
        # A request should NOT exist between user1 and user2
        request_exists = ProfileFriendRequest.objects.filter(
            models.Q(sender=self.profile1, receiver=self.profile2) |
            models.Q(sender=self.profile2, receiver=self.profile1)
        ).exists()
        self.assertFalse(request_exists)
        # Only the request from user3 to user1 should have been created
        self.assertEqual(ProfileFriendRequest.objects.count(), 1)
        self.assertTrue(ProfileFriendRequest.objects.filter(sender=self.profile3, receiver=self.profile1).exists())


    @patch(f'{LOGIC_MODULE_PATH}.random.sample')
    @patch(f'{LOGIC_MODULE_PATH}.random.randint')
    def test_skips_creating_request_if_request_already_exists(self, mock_randint, mock_sample):
        """
        Test that no duplicate friend request is created if one already exists.
        """
        # --- Setup ---
        # A pending request already exists from user1 to user2
        ProfileFriendRequest.objects.create(sender=self.profile1, receiver=self.profile2)
        self.assertEqual(ProfileFriendRequest.objects.count(), 1)
        
        # --- Setup Mocks ---
        mock_randint.return_value = 1
        # Force user1 to try sending to user2 again
        # And force user2 to try sending to user1 (reverse direction)
        mock_sample.side_effect = [
            [self.user2], # user1 -> user2 (should be skipped)
            [self.user1], # user2 -> user1 (should be skipped)
            [self.user1], # user3 -> user1 (should be created)
        ]
        
        # --- Action ---
        _create_pending_friend_requests(self.all_users)

        # --- Assertions ---
        # The total count should be 2 (the initial one + the one from user3)
        self.assertEqual(ProfileFriendRequest.objects.count(), 2)

    def test_no_self_requests_are_created(self):
        """
        Test that a user cannot send a friend request to themselves.
        (This is handled by the list comprehension, but this test verifies it.)
        """
        # In a list with only one user, the potential_receivers list will be empty
        # and the inner loop will never run, so no request can be created.
        _create_pending_friend_requests([self.user1])
        self.assertEqual(ProfileFriendRequest.objects.count(), 0)