"""
Test suite for WebSocket chat consumer functionality.

Tests the basic features of the chat consumer:
- Connection/disconnection
- Authentication and authorization
- Message sending/receiving
- Typing indicators
"""

import json
import logging
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from django.test import TestCase, TransactionTestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.urls import re_path

from ..consumers import ChatConsumer
from ..routing import websocket_urlpatterns
from ..models import ChatRoom, Message

# Import pytest if available (optional, for pytest-asyncio)
try:
    import pytest
except ImportError:
    pytest = None

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

# Set up test-specific channel layers
TEST_CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


User = get_user_model()


@override_settings(CHANNEL_LAYERS=TEST_CHANNEL_LAYERS)
class ChatConsumerTestCase(TransactionTestCase):
    """
    Test case for WebSocket chat consumer.

    Uses TransactionTestCase to handle the database transactions in async code.
    Uses an in-memory channel layer for testing.
    """

    def setUp(self):
        """Set up test data for each test."""
        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1", email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )
        self.unauthorized_user = User.objects.create_user(
            username="unauthorized",
            email="unauthorized@example.com",
            password="testpass123",
        )

        # Create test chat room
        self.chat_room = ChatRoom.objects.create(
            name="Test Room", room_type="GROUP", creator=self.user1
        )

        # Add authorized users to room
        self.chat_room.participants.add(self.user1, self.user2)

        # Set up application for testing
        self.application = URLRouter(websocket_urlpatterns)


class ConnectionTests(ChatConsumerTestCase):
    """Tests for WebSocket connection handling."""

    async def test_connect_authorized(self):
        """Test connection with authorized user."""
        # Create WebSocket communicator with the application from routing
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        # Add user to scope (as middleware would)
        communicator.scope["user"] = self.user1

        # Connect to WebSocket with longer timeout
        connected, subprotocol = await communicator.connect(timeout=3)

        # Assert connection successful
        self.assertTrue(connected)

        # Clean up
        await communicator.disconnect()

    async def test_connect_unauthorized(self):
        """Test connection rejection for unauthorized user."""
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator.scope["user"] = self.unauthorized_user

        # Attempt to connect
        connected, subprotocol = await communicator.connect(timeout=3)

        # Assert connection rejected
        self.assertFalse(connected)

    async def test_connect_unauthenticated(self):
        """Test connection rejection for unauthenticated user."""
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        # No user in scope (unauthenticated)

        # Attempt to connect
        connected, subprotocol = await communicator.connect(timeout=3)

        # Assert connection rejected
        self.assertFalse(connected)

    async def test_connect_nonexistent_room(self):
        """Test connection rejection for non-existent room."""
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/999999/"  # Non-existent room ID
        )
        communicator.scope["user"] = self.user1

        # Attempt to connect
        connected, subprotocol = await communicator.connect(timeout=3)

        # Assert connection rejected
        self.assertFalse(connected)

    async def test_disconnect_removes_from_group(self):
        """Test that disconnected users are properly removed from the room group."""
        # Connect first user
        communicator1 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator1.scope["user"] = self.user1
        connected1, _ = await communicator1.connect(timeout=3)
        self.assertTrue(connected1)

        # Disconnect user
        await communicator1.disconnect()

        # Connect second user
        communicator2 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator2.scope["user"] = self.user2
        connected2, _ = await communicator2.connect(timeout=3)
        self.assertTrue(connected2)

        # Send message from second user
        await communicator2.send_json_to(
            {"type": "chat_message", "message": "Test message after disconnect"}
        )

        # User1 should NOT receive the message (would raise TimeoutError)
        with self.assertRaises(asyncio.TimeoutError):
            await communicator1.receive_json_from(timeout=1)

        # Clean up
        await communicator2.disconnect()


class MessageTests(ChatConsumerTestCase):
    """Tests for WebSocket message handling."""

    async def test_send_and_receive_message(self):
        """Test sending and receiving a chat message."""
        # Connect user1
        communicator1 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator1.scope["user"] = self.user1
        connected1, _ = await communicator1.connect(timeout=3)
        self.assertTrue(connected1)

        # Connect user2
        communicator2 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator2.scope["user"] = self.user2
        connected2, _ = await communicator2.connect(timeout=3)
        self.assertTrue(connected2)

        # User1 sends a message
        test_message = "Hello, this is a test message!"
        await communicator1.send_json_to(
            {"type": "chat_message", "message": test_message}
        )

        # Both users should receive the message
        response1 = await communicator1.receive_json_from(timeout=3)
        response2 = await communicator2.receive_json_from(timeout=3)

        # Assert message received by both users
        self.assertEqual(response1["type"], "chat_message")
        self.assertEqual(response2["type"], "chat_message")
        self.assertEqual(response1["message"]["content"], test_message)
        self.assertEqual(response2["message"]["content"], test_message)
        # The sender field is a StringRelatedField in MessageSerializer
        self.assertEqual(response1["message"]["sender"], self.user1.username)
        self.assertEqual(response2["message"]["sender"], self.user1.username)

        # Verify message was saved to database
        messages = await database_sync_to_async(
            lambda: list(
                Message.objects.filter(
                    content=test_message, sender=self.user1, chat_room=self.chat_room
                )
            )
        )()
        self.assertEqual(len(messages), 1)

        # Clean up
        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_empty_message_handling(self):
        """Test handling of empty messages."""
        # Connect user
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator.scope["user"] = self.user1
        connected, _ = await communicator.connect(timeout=3)
        self.assertTrue(connected)

        # Send empty message
        await communicator.send_json_to({"type": "chat_message", "message": ""})

        # Should receive error
        response = await communicator.receive_json_from(timeout=3)

        # Assert error received
        self.assertEqual(response["type"], "error")
        self.assertIn("empty", response["error"].lower())

        # Clean up
        await communicator.disconnect()

    async def test_long_message_handling(self):
        """Test handling of messages that exceed length limit."""
        # Connect user
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator.scope["user"] = self.user1
        connected, _ = await communicator.connect(timeout=3)
        self.assertTrue(connected)

        # Create message that exceeds 1000 character limit
        long_message = "x" * 1001

        # Send long message
        await communicator.send_json_to(
            {"type": "chat_message", "message": long_message}
        )

        # Should receive error
        response = await communicator.receive_json_from(timeout=3)

        # Assert error received
        self.assertEqual(response["type"], "error")
        self.assertIn("too long", response["error"].lower())

        # Clean up
        await communicator.disconnect()

    async def test_invalid_json(self):
        """Test handling of invalid JSON."""
        # Connect user
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator.scope["user"] = self.user1
        connected, _ = await communicator.connect(timeout=3)
        self.assertTrue(connected)

        # Send invalid JSON
        await communicator.send_to(text_data="not valid json")

        # Should receive error
        response = await communicator.receive_json_from(timeout=3)

        # Assert error received
        self.assertEqual(response["type"], "error")
        self.assertIn("invalid", response["error"].lower())

        # Clean up
        await communicator.disconnect()


class TypingIndicatorTests(ChatConsumerTestCase):
    """Tests for typing indicator functionality."""

    async def test_typing_indicator(self):
        """Test typing indicator broadcast."""
        # Connect user1
        communicator1 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator1.scope["user"] = self.user1
        connected1, _ = await communicator1.connect(timeout=3)
        self.assertTrue(connected1)

        # Connect user2
        communicator2 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator2.scope["user"] = self.user2
        connected2, _ = await communicator2.connect(timeout=3)
        self.assertTrue(connected2)

        # User1 sends typing indicator
        await communicator1.send_json_to(
            {"type": "typing_indicator", "is_typing": True}
        )

        # User2 should receive typing indicator
        response = await communicator2.receive_json_from(timeout=3)

        # Assert typing indicator received
        self.assertEqual(response["type"], "typing_indicator")
        self.assertEqual(response["user_id"], self.user1.id)
        self.assertTrue(response["is_typing"])

        # User1 should not receive their own typing indicator
        with self.assertRaises(asyncio.TimeoutError):
            await communicator1.receive_json_from(timeout=1)

        # Clean up
        await communicator1.disconnect()
        await communicator2.disconnect()

    async def test_typing_stop_indicator(self):
        """Test typing stopped indicator."""
        # Connect both users
        communicator1 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator1.scope["user"] = self.user1
        connected1, _ = await communicator1.connect(timeout=3)
        self.assertTrue(connected1)

        communicator2 = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator2.scope["user"] = self.user2
        connected2, _ = await communicator2.connect(timeout=3)
        self.assertTrue(connected2)

        # User1 sends typing indicator (stopped typing)
        await communicator1.send_json_to(
            {"type": "typing_indicator", "is_typing": False}
        )

        # User2 should receive typing indicator
        response = await communicator2.receive_json_from(timeout=3)

        # Assert typing indicator received
        self.assertEqual(response["type"], "typing_indicator")
        self.assertEqual(response["user_id"], self.user1.id)
        self.assertFalse(response["is_typing"])

        # Clean up
        await communicator1.disconnect()
        await communicator2.disconnect()


class UnsupportedMessageTypeTests(ChatConsumerTestCase):
    """Tests for handling unsupported message types."""

    async def test_unsupported_message_type(self):
        """Test handling of unsupported message type."""
        # Connect user
        communicator = WebsocketCommunicator(
            self.application, f"/ws/chat/{self.chat_room.id}/"
        )
        communicator.scope["user"] = self.user1
        connected, _ = await communicator.connect(timeout=3)
        self.assertTrue(connected)

        # Send unsupported message type
        await communicator.send_json_to(
            {"type": "unsupported_type", "data": "test data"}
        )

        # Should receive error
        response = await communicator.receive_json_from(timeout=3)

        # Assert error received
        self.assertEqual(response["type"], "error")
        self.assertIn("unsupported", response["error"].lower())

        # Clean up
        await communicator.disconnect()
