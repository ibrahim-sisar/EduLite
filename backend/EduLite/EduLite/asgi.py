"""
ASGI config for EduLite project following Django security best practices.

Uses django-channels-jwt for secure WebSocket authentication without
exposing JWT tokens in query parameters.
"""

import os
import django
from django.core.asgi import get_asgi_application

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EduLite.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import chat.routing
from chat.auth_middleware import JWTAuthMiddlewareStack

# Create ASGI application following Django patterns
application = ProtocolTypeRouter(
    {
        # HTTP requests handled by Django
        "http": get_asgi_application(),
        # WebSocket connections with secure JWT authentication
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns))
        ),
    }
)
