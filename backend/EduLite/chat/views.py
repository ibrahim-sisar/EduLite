from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ChatRoom, Message
from .serializers import MessageSerializer, ChatRoomSerializer
from .permissions import IsParticipant, IsMessageSenderOrReadOnly
from .pagination import ChatRoomPagination, MessageCursorPagination


class ChatAppBaseAPIView(APIView):
    """
    A custom base API view for the Chat app.
    Provides default authentication permissions and a helper method to get serializer context.
    Other common functionalities for Chat APIViews can be added here.

    **attribute** 'permission_classes' is set to [IsAuthenticated] by default.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        """
        return {"request": self.request}


class ChatRoomListCreateView(ChatAppBaseAPIView):
    """
    API view to list chat rooms the authenticated user is part of or create a new chat room.

    GET:
    - Returns a paginated list of chat rooms where the authenticated user is a participant.

    POST:
    - Creates a new chat room and automatically adds the creator as a participant.

    Responses:
    - 200: Successfully retrieved the list of chat rooms.
    - 201: Successfully created a new chat room.
    - 400: Invalid data provided for creating a chat room.
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = ChatRoomPagination

    def get(self, request, *args, **kwargs):
        """List chat rooms where user is a participant"""
        queryset = ChatRoom.objects.filter(participants=request.user)

        # Initialize paginator and paginate queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        
        # Serialize paginated data
        serializer = ChatRoomSerializer(
            paginated_queryset, 
            many=True, 
            context=self.get_serializer_context()
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """Create a new chat room and add creator as participant"""
        serializer = ChatRoomSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            chat_room = serializer.save()
            chat_room.participants.add(request.user)
            return Response(
                ChatRoomSerializer(chat_room, context=self.get_serializer_context()).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomDetailView(ChatAppBaseAPIView):
    """
    API view to retrieve details for a specific chat room.

    GET:
    - Returns details of a chat room if the authenticated user is a participant.

    Path Parameters:
    - `pk` (int): The primary key of the chat room.

    Responses:
    - 200: Chat room details successfully retrieved.
    - 404: Chat room not found or user is not a participant.
    """
    permission_classes = [IsAuthenticated, IsParticipant]
    
    def get_object(self, pk):
        """Helper method to retrieve the chat room object or raise a 404 error"""
        return get_object_or_404(ChatRoom.objects.all(), pk=pk)

    def get(self, request, pk, *args, **kwargs):
        """Retrieve details of a specific chat room"""
        chat_room = self.get_object(pk)
        self.check_object_permissions(request, chat_room)
        serializer = ChatRoomSerializer(chat_room, context=self.get_serializer_context())
        return Response(serializer.data)


class MessageListCreateView(ChatAppBaseAPIView):
    """
    API view to list and create messages in a specific chat room.

    GET:
    - Returns a paginated list of messages in a chat room.

    POST:
    - Creates a new message in the chat room.

    Path Parameters:
    - `chat_room_id` (int): The ID of the chat room.

    Responses:
    - 200: Successfully retrieved the list of messages.
    - 201: Successfully created a new message.
    - 400: Invalid data provided for creating a message.
    """
    permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]
    pagination_class = MessageCursorPagination

    def get_chat_room(self, chat_room_id):
        """Helper method to retrieve the chat room object"""
        return get_object_or_404(
            ChatRoom.objects.all(),
            id=chat_room_id,
            participants=self.request.user
        )

    def get(self, request, chat_room_id, *args, **kwargs):
        """
        List messages for a specific chat room.
        """
        chat_room = self.get_chat_room(chat_room_id)
        
        queryset = Message.objects.filter(
            chat_room=chat_room
        ).select_related("sender", "chat_room")
        
        # Initialize paginator and paginate queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        
        # Serialize paginated data
        serializer = MessageSerializer(
            paginated_queryset, 
            many=True, 
            context=self.get_serializer_context()
        )
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, chat_room_id, *args, **kwargs):
        """Create a new message in the chat room"""
        # Verify chat room exists and user is participant
        chat_room = self.get_chat_room(chat_room_id)
        
        serializer = MessageSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            message = serializer.save(
                chat_room=chat_room,
                sender=request.user
            )
            return Response(
                MessageSerializer(message, context=self.get_serializer_context()).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


""" Retrieve a specific message in a chat room (Message sender can update/delete)"""


class MessageDetailView(ChatAppBaseAPIView):
    """
    API view to manage a specific message in a chat room.

    GET:
    - Retrieve a specific message.

    PUT:
    - Update a message (full update, sender only).

    PATCH:
    - Partially update a message (sender only).

    DELETE:
    - Delete a message (sender only).

    Path Parameters:
    - `chat_room_id` (int): The ID of the chat room.
    - `pk` (int): The ID of the message.

    Responses:
    - 200: Successfully retrieved or updated the message.
    - 204: Successfully deleted the message.
    - 400: Invalid data provided for updating the message.
    - 404: Message not found or user is not authorized.
    """
    permission_classes = [IsAuthenticated, IsMessageSenderOrReadOnly]

    def get_object(self, chat_room_id, message_id):
        """Helper method to retrieve the message object or raise a 404 error"""
        return get_object_or_404(
            Message.objects.select_related("sender", "chat_room"),
            id=message_id,
            chat_room__id=chat_room_id,
            chat_room__participants=self.request.user
        )

    def get(self, request, chat_room_id, pk, *args, **kwargs):
        """Retrieve a specific message"""
        message = self.get_object(chat_room_id, pk)
        serializer = MessageSerializer(message, context=self.get_serializer_context())
        return Response(serializer.data)

    def put(self, request, chat_room_id, pk, *args, **kwargs):
        """Update a message (full update)"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        
        serializer = MessageSerializer(
            message,
            data=request.data,
            context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, chat_room_id, pk, *args, **kwargs):
        """Update a message (partial update)"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        
        serializer = MessageSerializer(
            message,
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, chat_room_id, pk, *args, **kwargs):
        """Delete a message"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        message.delete()
        return Response(
            {"message": "Message deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
