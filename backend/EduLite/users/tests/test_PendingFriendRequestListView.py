from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import UserProfile, ProfileFriendRequest

User = get_user_model()


class PendingFriendRequestListViewTests(APITestCase):
    """
    Test suite for the PendingFriendRequestListView.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Define the URL for the view
        cls.list_url = reverse("friend-request-pending-list")

        # Create users and their profiles
        cls.user_a = User.objects.create_user(username="user_a", password="password123")
        cls.profile_a = UserProfile.objects.get(user=cls.user_a)

        cls.user_b = User.objects.create_user(username="user_b", password="password123")
        cls.profile_b = UserProfile.objects.get(user=cls.user_b)

        cls.user_c = User.objects.create_user(username="user_c", password="password123")
        cls.profile_c = UserProfile.objects.get(user=cls.user_c)

        # Create friend requests to establish relationships
        # 1. User A sends a request to User B
        ProfileFriendRequest.objects.create(
            sender=cls.profile_a, receiver=cls.profile_b
        )
        # 2. User C sends a request to User B
        ProfileFriendRequest.objects.create(
            sender=cls.profile_c, receiver=cls.profile_b
        )
        # 3. User B sends a request to User C
        ProfileFriendRequest.objects.create(
            sender=cls.profile_b, receiver=cls.profile_c
        )

    def test_list_requires_authentication(self):
        """Test that unauthenticated users cannot list pending requests."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_received_requests_by_default(self):
        """Test that GET without params defaults to listing received requests."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User B should have received 2 requests (from A and C)
        self.assertEqual(response.data["count"], 2)
        # Verify the senders are correct
        sender_usernames = {item["sender_id"] for item in response.data["results"]}
        self.assertEqual(sender_usernames, {1, 3})

    def test_list_received_requests_explicitly(self):
        """Test listing received requests with '?direction=received'."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_url, {"direction": "received"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_list_sent_requests(self):
        """Test listing sent requests with '?direction=sent'."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_url, {"direction": "sent"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User B sent 1 request (to C)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["receiver_id"], self.profile_c.user.id
        )

    def test_list_with_invalid_direction(self):
        """Test that an invalid direction parameter returns an empty list."""
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_url, {"direction": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_list_when_no_requests_exist(self):
        """Test listing requests for a user with no activity."""
        # User A has only sent requests, so they should have no received requests
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.list_url, {"direction": "received"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_response_data_serialization_format(self):
        """
        Test that the response data for a request item is serialized correctly.
        """
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data["count"], 0)

        first_result = response.data["results"][0]
        # Check for key fields defined in ProfileFriendRequestSerializer
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
        self.assertEqual(set(first_result.keys()), set(expected_keys))

    def test_list_is_paginated(self):
        """Test that the request list is paginated."""
        # Authenticate as a user who will receive many requests
        self.client.force_authenticate(user=self.user_a)

        # Create more requests than the default page size (e.g., 12)
        for i in range(12):
            sender_user = User.objects.create_user(
                username=f"many_sender_{i}", password="password123"
            )
            sender_profile = UserProfile.objects.get(user=sender_user)
            ProfileFriendRequest.objects.create(
                sender=sender_profile, receiver=self.profile_a
            )

        response = self.client.get(self.list_url, {"direction": "received"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        # Assumes PageNumberPagination default page size is 10 or set in the view
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_list_direction_is_case_insensitive(self):
        """Test that the 'direction' query parameter is case-insensitive."""
        self.client.force_authenticate(user=self.user_b)

        # Test with 'SENT' instead of 'sent'
        response = self.client.get(self.list_url, {"direction": "SENT"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User B sent 1 request, so the count should be 1
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["receiver_id"], self.profile_c.user.id
        )
