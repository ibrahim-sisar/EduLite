"""Authentication classes for channels."""

from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from jwt import decode as jwt_decode

User = get_user_model()


class JWTAuthMiddleware:
    """Middleware to authenticate user for channels (supports header + query param)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Authenticate user from JWT in query param or Authorization header."""
        close_old_connections()
        token = None

        try:
            # --- 1. Try from query param ?token= ---
            query_params = parse_qs(scope["query_string"].decode("utf8"))
            token_list = query_params.get("token")
            if token_list:
                token = token_list[0]

            # --- 2. Try from headers if no query param ---
            if not token:
                headers = dict(scope.get("headers", []))
                auth_header = headers.get(b"authorization")
                if auth_header:
                    auth_header = auth_header.decode("utf8")
                    if auth_header.startswith("Bearer "):
                        token = auth_header.split("Bearer ")[1]

            # --- 3. Decode token if found ---
            if token:
                data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                scope["user"] = await self.get_user(data.get("user_id"))
            else:
                scope["user"] = AnonymousUser()

        except (InvalidSignatureError, ExpiredSignatureError, DecodeError) as e:
            # Invalid token → fallback to anonymous
            print(f"JWT authentication error: {str(e)}")
            scope["user"] = AnonymousUser()
        except Exception as e:
            print(f"Unexpected authentication error: {str(e)}")
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        """Return the user based on user id."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()


def JWTAuthMiddlewareStack(app):
    """Wrap default AuthMiddlewareStack with JWTAuthMiddleware."""
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
