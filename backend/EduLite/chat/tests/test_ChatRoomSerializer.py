import logging
import pprint
from django.test import TestCase
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message
from chat.serializers import ChatRoomSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatRoomSerializerTest(TestCase):
    @classmethod
    def setUpClass(cls): 
        super().setUpClass()
        logger.info(
            "\n--- ChatRoomSerializerTest.setUpClass() ---\n"
        )
    
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
        logger.debug(
            "test_chatroom_serializer_read_fields()"
            "\n--\tSerialized data for ChatRoom ID %s:\n\t\t%s"  
            "\n--\tSerialized messages within data: %s",       
            self.chat_room.id,                                 
            data,                              
            data.get('messages')                               
        )
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
        logger.debug(
            "\ntest_chatroom_serializer_write()\n"
            "--\tPayload for creating new chat_room: \n\t\t%s\n"
            
            "--\tChatRoom created successfully:\n"
            "\t\tID: %s\n"
            "\t\tName: '%s'\n"
            "\t\tType: %s\n"
            "\t\tParticipants count: %s\n"
            "\t\tParticipants (IDs): %s",
            payload,
            chat_room.id,
            chat_room.name,
            chat_room.room_type,
            chat_room.participants.count(),
            list(chat_room.participants.values_list('id', flat=True))
        )
        self.assertEqual(chat_room.name, "Another Chat")
        self.assertEqual(chat_room.room_type, 'GROUP')
        self.assertCountEqual(list(chat_room.participants.all()), [self.user1, self.user2])
