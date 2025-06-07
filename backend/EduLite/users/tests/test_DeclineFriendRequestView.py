from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import UserProfile, ProfileFriendRequest

User = get_user_model()

class DeclineFriendRequestViewTests(APITestCase):
    """
    Test suite for the DeclineFriendRequestView.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users and get their profiles (created via signal)
        cls.user_sender = User.objects.create_user(username='sender_user', password='password123')
        cls.profile_sender = UserProfile.objects.get(user=cls.user_sender)

        cls.user_receiver = User.objects.create_user(username='receiver_user', password='password123')
        cls.profile_receiver = UserProfile.objects.get(user=cls.user_receiver)

        cls.user_unrelated = User.objects.create_user(username='unrelated_user', password='password123')
        cls.profile_unrelated = UserProfile.objects.get(user=cls.user_unrelated)
        
        # Create a persistent friend request for most tests
        cls.friend_request = ProfileFriendRequest.objects.create(
            sender=cls.profile_sender,
            receiver=cls.profile_receiver
        )
        cls.decline_url = reverse('friend-request-decline', kwargs={'request_pk': cls.friend_request.pk})

    def test_decline_request_unauthenticated(self):
        """
        Test that an unauthenticated user cannot decline a friend request.
        """
        response = self.client.post(self.decline_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receiver_can_decline_request(self):
        """
        Test that the intended receiver of a request can successfully decline it.
        """
        self.client.force_authenticate(user=self.user_receiver)
        response = self.client.post(self.decline_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Friend request declined successfully.")

        # Verify the request object has been deleted
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=self.friend_request.pk)

    def test_sender_can_cancel_request(self):
        """
        Test that the original sender of a request can successfully cancel it.
        """
        self.client.force_authenticate(user=self.user_sender)
        response = self.client.post(self.decline_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Friend request canceled successfully.")

        # Verify the request object has been deleted
        self.assertFalse(ProfileFriendRequest.objects.filter(pk=self.friend_request.pk).exists())

    def test_unrelated_user_cannot_decline_request(self):
        """
        Test that a user who is neither the sender nor the receiver cannot decline the request.
        """
        self.client.force_authenticate(user=self.user_unrelated)
        response = self.client.post(self.decline_url)
        # This tests the IsFriendRequestReceiverOrSender permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_nonexistent_request(self):
        """
        Test that attempting to decline a request that doesn't exist returns a 404.
        """
        self.client.force_authenticate(user=self.user_sender)
        nonexistent_url = reverse('friend-request-decline', kwargs={'request_pk': 9999})
        response = self.client.post(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_already_actioned_request(self):
        """
        Test that declining a request that was already declined/accepted results in a 404.
        """
        # First, the receiver declines the request successfully
        self.client.force_authenticate(user=self.user_receiver)
        self.client.post(self.decline_url)

        # Now, the sender tries to cancel the same, now-deleted request
        self.client.force_authenticate(user=self.user_sender)
        response = self.client.post(self.decline_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_with_get_method_not_allowed(self):
        """
        Test that using GET on the decline endpoint is not allowed.
        """
        self.client.force_authenticate(user=self.user_receiver)
        response = self.client.get(self.decline_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_decline_with_put_method_not_allowed(self):
        """
        Test that using PUT on the decline endpoint is not allowed.
        """
        self.client.force_authenticate(user=self.user_receiver)
        response = self.client.put(self.decline_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)