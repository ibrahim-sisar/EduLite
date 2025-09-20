from rest_framework import permissions
from .models import ChatRoom


class IsParticipant(permissions.BasePermission):
    """
    Custom permission class to control ChatRoom access.

    Allows:
    - Participants: Full access to rooms they are part of
    - Others: No access
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow access only for Chat Room participants
        return obj.participants.filter(id=request.user.id).exists()


class IsMessageSenderOrReadOnly(permissions.BasePermission):
    """
    Custom permission class to control Message access.

    Allows:
    - Message Sender: Full access (read/write/delete) to their own messages
    - Chat Participants: Read-only access to messages in their rooms
    - Others: No access
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        chat_room_id = view.kwargs.get("chat_room_id")
        return ChatRoom.objects.filter(
            id=chat_room_id, participants=request.user
        ).exists()

    def has_object_permission(self, request, view, obj):
        # Allow read access for chat participants
        if request.method in permissions.SAFE_METHODS:
            return obj.chat_room.participants.filter(id=request.user.id).exists()

        # Write/Delete permissions only for message sender
        return obj.sender == request.user


class IsChatRoomManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators and editors to manage chat room.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any participant
        if request.method in permissions.SAFE_METHODS:
            return obj.participants.filter(id=request.user.id).exists()

        # Write permissions are only allowed to creators and editors
        return obj.is_creator(request.user) or obj.is_editor(request.user)
