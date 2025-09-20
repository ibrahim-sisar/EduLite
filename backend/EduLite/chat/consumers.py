# chat/consumers.py - WebSocket consumers for real-time chat functionality
# Handles WebSocket connections, authentication, and message broadcasting


"""
WebSocket consumers for EduLite chat functionality.

"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .models import ChatRoom, Message
from .serializers import MessageSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.room_group_name = None
        self.user = None
        self.chat_room = None
        self.last_activity = None

    async def connect(self):
        """Handle WebSocket connection."""
        # Extract authenticated user from middleware
        self.user = self.scope.get("user")

        # Record last activity timestamp
        self.last_activity = timezone.now()

        if not self.user or isinstance(self.user, AnonymousUser):
            logger.warning(f"WebSocket connection rejected: unauthenticated user")
            await self.close(code=4001)  # Unauthorized
            return

        # Extract room ID from URL
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Validate room access
        self.chat_room = await self.get_chat_room()
        if not self.chat_room:
            logger.warning(
                f"WebSocket connection rejected: room {self.room_id} not found"
            )
            await self.close(code=4004)  # Not Found
            return

        if not await self.has_room_permission():
            logger.warning(
                f"WebSocket connection rejected: user {self.user.id} lacks permission for room {self.room_id}"
            )
            await self.close(code=4003)  # Forbidden
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        logger.info(
            f"WebSocket connected: user {self.user.id} joined room {self.room_id}"
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, "room_group_name") and self.room_group_name:
            # Remove from room group
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

            logger.info(
                f"WebSocket disconnected: user {getattr(self.user, 'id', 'unknown')} left room {self.room_id}, code: {close_code}"
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            # Update last activity timestamp
            self.last_activity = timezone.now()

            data = json.loads(text_data)
            message_type = data.get("type")

            # Handle different message types
            if message_type == "chat_message":
                await self.handle_chat_message(data)
            elif message_type == "typing_indicator":
                await self.handle_typing_indicator(data)
            else:
                logger.warning(
                    f"Unsupported message type: {message_type} from user {self.user.id}"
                )
                await self.send_error("Unsupported message type")

        except json.JSONDecodeError as e:
            logger.warning(
                f"Invalid JSON from user {getattr(self.user, 'id', 'unknown')}: {str(e)}"
            )
            await self.send_error("Invalid message format")

    async def handle_chat_message(self, data):
        """Handle chat message from client."""
        message_content = data.get("message", "").strip()

        if not message_content:
            logger.debug(f"Empty message received from user {self.user.id}")
            await self.send_error("Message content cannot be empty")
            return

        # Check for message length
        max_length = 1000  # Maximum character limit
        if len(message_content) > max_length:
            logger.debug(
                f"Message too long ({len(message_content)} chars) from user {self.user.id}"
            )
            await self.send_error(f"Message too long (maximum {max_length} characters)")
            return

        # Save message to database
        try:
            message = await self.save_message(message_content)
            logger.debug(f"Message saved: {message.id} from user {self.user.id}")
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            await self.send_error("Failed to save message")
            return
        message_data = await self.get_serialized_message(message)

        # Broadcast message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message_broadcast", "message": message_data},
        )

    async def chat_message_broadcast(self, event):
        """Send chat message to WebSocket client."""
        await self.send(
            text_data=json.dumps({"type": "chat_message", "message": event["message"]})
        )

    async def handle_typing_indicator(self, data):
        """Handle typing indicator from client."""
        is_typing = data.get("is_typing", False)

        # Broadcast typing status to room (except sender)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_indicator_broadcast",
                "user_id": self.user.id,
                "username": getattr(self.user, "username", "Unknown"),
                "is_typing": is_typing,
            },
        )
        logger.debug(f"Typing indicator: user {self.user.id}, is_typing={is_typing}")

    async def typing_indicator_broadcast(self, event):
        """Broadcast typing indicator to clients."""
        # Don't send typing indicator back to the user who is typing
        if str(event["user_id"]) != str(getattr(self.user, "id", None)):
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing_indicator",
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "is_typing": event["is_typing"],
                    }
                )
            )

    @database_sync_to_async
    def get_chat_room(self):
        """Get chat room from database."""
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def has_room_permission(self):
        """Check if user has permission to access room."""
        try:
            return self.chat_room.participants.filter(id=self.user.id).exists()
        except Exception:
            return False

    @database_sync_to_async
    def save_message(self, content):
        """Save message to database."""
        return Message.objects.create(
            chat_room=self.chat_room, sender=self.user, content=content
        )

    @database_sync_to_async
    def get_serialized_message(self, message):
        """Serialize message using MessageSerializer."""
        return MessageSerializer(message).data

    # --- Utility Methods ---

    async def send_error(self, error_message):
        """
        Send error message to WebSocket client.

        Args:
            error_message: Error description
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "error",
                    "error": error_message,
                    "timestamp": timezone.now().isoformat(),
                }
            )
        )
