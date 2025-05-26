from django.test import TestCase
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message
from chat.serializers import ChatRoomSerializer

User = get_user_model()

class ChatRoomSerializerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', email='user1@example.com', password='password123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', email='user2@example.com', password='password123'
        )
        self.chat_room = ChatRoom.objects.create(
            name="Group Chat", room_type='GROUP'
        )
        self.chat_room.participants.set([self.user1, self.user2])
        self.message1 = Message.objects.create(
            chat_room=self.chat_room, sender=self.user1, content="First message"
        )

    def test_chatroom_serializer_read_fields(self):
        """Test that the serializer returns the correct fields and nested messages on read"""
        serializer = ChatRoomSerializer(self.chat_room)
        data = serializer.data
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('room_type', data)
        self.assertIn('participants', data)
        self.assertIn('messages', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['content'], "First message")

    def test_chatroom_serializer_write(self):
        """Test that the serializer can create a chat room with participants"""
        payload = {
            'name': "Another Chat",
            'room_type': 'GROUP',
            'participants': [self.user1.id, self.user2.id]
        }
        serializer = ChatRoomSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        chat_room = serializer.save()
        self.assertEqual(chat_room.name, "Another Chat")
        self.assertEqual(chat_room.room_type, 'GROUP')
        self.assertCountEqual(list(chat_room.participants.all()), [self.user1, self.user2])
