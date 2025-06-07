from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import UserProfile, ProfileFriendRequest

User = get_user_model()

class SendFriendRequestViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_sender = User.objects.create_user(username='sender', password='password123')
        cls.profile_sender = UserProfile.objects.get(user=cls.user_sender) # Assuming signal creates profile

        cls.user_receiver = User.objects.create_user(username='receiver', password='password123')
        cls.profile_receiver = UserProfile.objects.get(user=cls.user_receiver)
        
        cls.user_already_friend = User.objects.create_user(username='already_friend', password='password123')
        cls.profile_already_friend = UserProfile.objects.get(user=cls.user_already_friend)

        cls.send_request_url = reverse('friend-request-send') # Ensure this name matches your urls.py

    def setUp(self):
        self.client.force_authenticate(user=self.user_sender)

    def test_send_friend_request_successful(self):
        data = {'receiver_profile_id': self.profile_receiver.pk}
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProfileFriendRequest.objects.filter(
            sender=self.profile_sender,
            receiver=self.profile_receiver
        ).exists())
        # Check response data structure based on your ProfileFriendRequestSerializer
        self.assertIn('id', response.data)
        self.assertEqual(response.data['sender_id'], self.profile_sender.user.id) # Or username if serializer outputs that

    def test_send_request_missing_receiver_id(self):
        response = self.client.post(self.send_request_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "receiver_profile_id is required.")

    def test_send_request_invalid_receiver_id(self):
        from rest_framework.exceptions import ErrorDetail

        data = {'receiver_profile_id': 99999} # Non-existent PK
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], ErrorDetail(string='No UserProfile matches the given query.', code='not_found'))
        
    def test_send_request_to_self(self):
        data = {'receiver_profile_id': self.profile_sender.pk} # Sending to self
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You cannot send a friend request to yourself.")

    def test_send_request_to_existing_friend(self):
        # Make them friends first
        self.profile_sender.friends.add(self.profile_already_friend.user)
        
        data = {'receiver_profile_id': self.profile_already_friend.pk}
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You are already friends with this user.")

    def test_send_request_when_request_already_sent(self):
        # Send one request
        ProfileFriendRequest.objects.create(sender=self.profile_sender, receiver=self.profile_receiver)
        
        # Try to send again
        data = {'receiver_profile_id': self.profile_receiver.pk}
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You have already sent a friend request to this user.")

    def test_send_request_when_request_already_received(self):
        # A request exists from receiver to sender
        ProfileFriendRequest.objects.create(sender=self.profile_receiver, receiver=self.profile_sender)
        
        # Sender tries to send to receiver
        data = {'receiver_profile_id': self.profile_receiver.pk}
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "This user has already sent you a friend request. Check your pending requests.")


    def test_send_request_with_invalid_receiver_id_type(self):
        """
        Test sending a request where receiver_profile_id is not a valid integer.
        """
        data = {'receiver_profile_id': 'not-a-valid-integer'}
        response = self.client.post(self.send_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), "Invalid receiver_profile_id. Must be an integer.")
