"""
WebSocket routing configuration for chat functionality.

This module defines URL patterns for WebSocket connections following
Django's URL dispatcher patterns for consistency.
"""

from django.urls import re_path
from . import consumers

# WebSocket URL patterns following Django URL conventions
websocket_urlpatterns = [
    # # Simple echo consumer for testing (no authentication required)
    # re_path(r'ws/echo/$', consumers.EchoConsumer.as_asgi(), name='websocket_echo'),
    # # Ping-pong consumer for connection testing
    # re_path(r'ws/ping/$', consumers.PingPongConsumer.as_asgi(), name='websocket_ping'),
    # Production chat consumer with authentication
    re_path(
        r"ws/chat/(?P<room_id>[\w-]+)/$",
        consumers.ChatConsumer.as_asgi(),
        name="websocket_chat",
    ),
]
