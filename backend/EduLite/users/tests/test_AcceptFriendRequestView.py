from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import UserProfile, ProfileFriendRequest
from ..permissions import IsFriendRequestReceiver 

User = get_user_model()

class AcceptFriendRequestViewTests(APITestCase):
    """
    Test suite for the AcceptFriendRequestView.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole test class."""
        # Create users and their profiles
        cls.user_sender = User.objects.create_user(username='sender_user', password='password123')
        cls.profile_sender = UserProfile.objects.get(user=cls.user_sender)

        cls.user_receiver = User.objects.create_user(username='receiver_user', password='password123')
        cls.profile_receiver = UserProfile.objects.get(user=cls.user_receiver)

        cls.user_unrelated = User.objects.create_user(username='unrelated_user', password='password123')
        
        # Create a friend request from sender to receiver
        cls.friend_request = ProfileFriendRequest.objects.create(
            sender=cls.profile_sender,
            receiver=cls.profile_receiver
        )
        
        # Define the URL for the accept action
        cls.accept_url = reverse('friend-request-accept', kwargs={'request_pk': cls.friend_request.pk})

    def test_accept_request_unauthenticated(self):
        """
        Test that an unauthenticated user cannot accept a friend request.
        """
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receiver_can_accept_request(self):
        """
        Test that the intended receiver can successfully accept a friend request.
        """
        # Authenticate as the receiver
        self.client.force_authenticate(user=self.user_receiver)
        response = self.client.post(self.accept_url)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Friend request accepted.")

        # Verify the request object has been deleted from the database
        with self.assertRaises(ProfileFriendRequest.DoesNotExist):
            ProfileFriendRequest.objects.get(pk=self.friend_request.pk)

        # Verify that the friendship is now established symmetrically
        self.profile_sender.refresh_from_db()
        self.profile_receiver.refresh_from_db()
        self.assertIn(self.user_receiver, self.profile_sender.friends.all())
        self.assertIn(self.user_sender, self.profile_receiver.friends.all())

    def test_sender_cannot_accept_request(self):
        """
        Test that the sender of a request cannot accept it themselves.
        """
        # Authenticate as the sender
        self.client.force_authenticate(user=self.user_sender)
        response = self.client.post(self.accept_url)

        # This tests the IsFriendRequestReceiver permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unrelated_user_cannot_accept_request(self):
        """
        Test that a user who is not party to the request cannot accept it.
        """
        # Authenticate as the unrelated user
        self.client.force_authenticate(user=self.user_unrelated)
        response = self.client.post(self.accept_url)

        # This also tests the IsFriendRequestReceiver permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_nonexistent_request(self):
        """
        Test that attempting to accept a request that doesn't exist returns a 404.
        """
        self.client.force_authenticate(user=self.user_receiver)
        nonexistent_url = reverse('friend-request-accept', kwargs={'request_pk': 9999})
        response = self.client.post(nonexistent_url)
        
        # get_object_or_404 in the view should handle this
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_accept_already_accepted_request(self):
        """
        Test that accepting a request that was already accepted results in a 404
        (because the request object is deleted).
        """
        # The receiver accepts the request successfully the first time
        self.client.force_authenticate(user=self.user_receiver)
        first_response = self.client.post(self.accept_url)
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        # Now, try to accept it again
        second_response = self.client.post(self.accept_url)
        # The friend_request object no longer exists, so get_object_or_404 should trigger
        self.assertEqual(second_response.status_code, status.HTTP_404_NOT_FOUND)