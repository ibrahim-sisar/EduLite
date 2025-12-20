from django.shortcuts import render, get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from .models import ChatRoom, Message, ChatRoomInvitation
from .serializers import MessageSerializer, ChatRoomSerializer
from .permissions import IsParticipant, IsMessageSenderOrReadOnly
from .pagination import ChatRoomPagination, MessageCursorPagination
from django.contrib.auth import get_user_model


User = get_user_model()


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


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Bearer token for authentication.",
        ),
    ],
)
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

    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated, IsParticipant]
    pagination_class = ChatRoomPagination

    def get_queryset(self):
        """ "Get the queryset of chat rooms where the user is a participant"""
        return (
            ChatRoom.objects.filter(participants=self.request.user)
            .select_related("creator")
            .prefetch_related("editors", "participants")
        )

    @extend_schema(
        # define parameters as we've overridden the base class
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page (max 50)",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="The response will be a paginated JSON object containing a list of all chat rooms the user participates in.",
                response=inline_serializer(
                    name="ChatRoomPaginatedResponse",
                    fields={
                        "next": serializers.URLField(allow_null=True),
                        "previous": serializers.URLField(allow_null=True),
                        "count": serializers.IntegerField(),
                        "total_pages": serializers.IntegerField(),
                        "current_page": serializers.IntegerField(),
                        "page_size": serializers.IntegerField(),
                        "results": ChatRoomSerializer(many=True),
                    },
                ),
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        """List chat rooms where user is a participant"""
        queryset = self.get_queryset()

        # Initialize paginator and paginate queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        # Serialize paginated data
        serializer = ChatRoomSerializer(
            paginated_queryset, many=True, context=self.get_serializer_context()
        )

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        parameters=[
            ChatRoomSerializer,
        ],
        responses={
            201: OpenApiResponse(
                description="The response will contain the details of the newly created chat room.",
                response=ChatRoomSerializer(),
            ),
            400: OpenApiResponse(
                description="Invalid data provided for creating a chat room.",
                response=inline_serializer(
                    name="ChatRoomValidationError",
                    fields={
                        "participants": serializers.ListField(
                            child=serializers.CharField()
                        ),
                        "room_type": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Invalid Participant",
                        value={"detail": 'Invalid pk "X" - object does not exist.'},
                    ),
                    OpenApiExample(
                        "Missing Room Type", value={"detail": "This field is required."}
                    ),
                    OpenApiExample(
                        "Invalid Room Type",
                        value={"detail": '"X" is not a valid choice.'},
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        """Create a new chat room and add creator as participant"""
        serializer = ChatRoomSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            chat_room = serializer.save()
            chat_room.participants.add(request.user)
            chat_room.editors.add(request.user)
            return Response(
                ChatRoomSerializer(
                    chat_room, context=self.get_serializer_context()
                ).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Bearer token for authentication.",
        ),
    ],
)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifyer for the chat room.",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="The response will contain the details of the chat room specified by `id`.",
                response=ChatRoomSerializer(),
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="A `Chat Room` with the specified `id` does not exist.",
                response=inline_serializer(
                    name="NotFoundError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "No ChatRoom matches the given query."},
                    )
                ],
            ),
        },
    )
    def get(self, request, pk, *args, **kwargs):
        """Retrieve details of a specific chat room"""
        chat_room = self.get_object(pk)
        self.check_object_permissions(request, chat_room)
        serializer = ChatRoomSerializer(
            chat_room, context=self.get_serializer_context()
        )
        return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Bearer token for authentication.",
        ),
    ],
)
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
            ChatRoom.objects.all(), id=chat_room_id, participants=self.request.user
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="chat_room_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the chat room.",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Number of results to return per page (default 50).",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Paginated list of chat room messages.",
                response=inline_serializer(
                    name="MessageListPaginatedResponse",
                    fields={
                        "next": serializers.URLField(allow_null=True),
                        "previous": serializers.URLField(allow_null=True),
                        "results": serializers.ListField(
                            child=inline_serializer(
                                name="Message",
                                fields={
                                    "id": serializers.IntegerField(),
                                    "chat_room": serializers.IntegerField(),
                                    "sender": serializers.CharField(),
                                    "sender_id": serializers.IntegerField(),
                                    "content": serializers.CharField(),
                                    "created_at": serializers.DateTimeField(),
                                    "is_read": serializers.BooleanField(),
                                },
                            )
                        ),
                    },
                ),
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
        },
    )
    def get(self, request, chat_room_id, *args, **kwargs):
        """
        List messages for a specific chat room.
        """
        chat_room = self.get_chat_room(chat_room_id)

        queryset = Message.objects.filter(chat_room=chat_room).select_related(
            "sender", "chat_room"
        )

        # Initialize paginator and paginate queryset
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        # Serialize paginated data
        serializer = MessageSerializer(
            paginated_queryset, many=True, context=self.get_serializer_context()
        )

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="chat_room_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the chat room.",
            ),
        ],
        request=inline_serializer(
            name="MessageCreateRequest",
            fields={
                "content": serializers.CharField(),
                "is_read": serializers.BooleanField(required=False, default=False),
            },
        ),
        responses={
            201: OpenApiResponse(
                description="Successfully created a new message in the chat room.",
                response=inline_serializer(
                    name="MessageDetail",
                    fields={
                        "id": serializers.IntegerField(),
                        "chat_room": serializers.IntegerField(),
                        "sender": serializers.CharField(),
                        "sender_id": serializers.IntegerField(),
                        "content": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                        "is_read": serializers.BooleanField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Created Message",
                        value={
                            "id": 15,
                            "chat_room": 1,
                            "sender": "edulite",
                            "sender_id": 1,
                            "content": "Hello everyone! How are you doing today?",
                            "created_at": "2023-10-01T14:30:00Z",
                            "is_read": False,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid data provided for creating a message.",
                response=inline_serializer(
                    name="MessageCreateError",
                    fields={
                        "content": serializers.ListField(child=serializers.CharField())
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Invalid Content",
                        value={"content": ["This field may not be blank."]},
                    ),
                    OpenApiExample(
                        "Missing Content",
                        value={"content": ["This field is required."]},
                    ),
                    OpenApiExample(
                        "Invalid is_read",
                        value={"is_read": ["Must be a valid boolean."]},
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
        },
    )
    def post(self, request, chat_room_id, *args, **kwargs):
        """Create a new message in the chat room"""
        # Verify chat room exists and user is participant
        chat_room = self.get_chat_room(chat_room_id)

        serializer = MessageSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            message = serializer.save(chat_room=chat_room, sender=request.user)
            return Response(
                MessageSerializer(message, context=self.get_serializer_context()).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


""" Retrieve a specific message in a chat room (Message sender can update/delete)"""


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=True,
            description="Bearer token for authentication.",
        ),
    ],
)
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
            chat_room__participants=self.request.user,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="chat_room_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the chat room.",
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the message.",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved message details.",
                response=inline_serializer(
                    name="MessageDetailResponse",
                    fields={
                        "id": serializers.IntegerField(),
                        "chat_room": serializers.IntegerField(),
                        "sender": serializers.CharField(),
                        "content": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                        "is_read": serializers.BooleanField(),
                    },
                ),
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Message not found.",
                response=inline_serializer(
                    name="NotFoundError",
                    fields={
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "No Message matches the given query."},
                    )
                ],
            ),
        },
    )
    def get(self, request, chat_room_id, pk, *args, **kwargs):
        """Retrieve a specific message in a chat room."""
        message = self.get_object(chat_room_id, pk)
        serializer = MessageSerializer(message, context=self.get_serializer_context())
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="chat_room_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the chat room.",
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the message.",
            ),
        ],
        request=inline_serializer(
            name="MessageUpdateRequest",
            fields={
                "content": serializers.CharField(),
            },
        ),
        responses={
            200: OpenApiResponse(
                description="Successfully updated message details.",
                response=inline_serializer(
                    name="MessageUpdateResponse",
                    fields={
                        "id": serializers.IntegerField(),
                        "chat_room": serializers.IntegerField(),
                        "sender": serializers.CharField(),
                        "content": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                        "is_read": serializers.BooleanField(),
                    },
                ),
            ),
            400: OpenApiResponse(
                description="The provided data is invalid (e.g., `content` field data empty).",
                response=inline_serializer(
                    name="MessageUpdateError",
                    fields={
                        "content": serializers.ListField(child=serializers.CharField())
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Invalid Content",
                        value={"content": ["This field may not be blank."]},
                    ),
                    OpenApiExample(
                        "Missing Content",
                        value={"content": ["This field is required."]},
                    ),
                    OpenApiExample(
                        "Invalid is_read",
                        value={"is_read": ["Must be a valid boolean."]},
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Message not found.",
                response=inline_serializer(
                    name="NotFoundError",
                    fields={
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "No Message matches the given query."},
                    )
                ],
            ),
        },
    )
    def put(self, request, chat_room_id, pk, *args, **kwargs):
        """Update a message (full update)."""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)

        serializer = MessageSerializer(
            message, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="chat_room_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the chat room.",
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the message.",
            ),
        ],
        request=inline_serializer(
            name="MessagePartialUpdateRequest",
            fields={"content": serializers.CharField(required=False)},
        ),
        responses={
            200: OpenApiResponse(
                description="Successfully updated message details partially.",
                response=inline_serializer(
                    name="MessagePartialUpdateResponse",
                    fields={
                        "id": serializers.IntegerField(),
                        "chat_room": serializers.IntegerField(),
                        "sender": serializers.CharField(),
                        "content": serializers.CharField(),
                        "created_at": serializers.DateTimeField(),
                        "is_read": serializers.BooleanField(),
                    },
                ),
            ),
            400: OpenApiResponse(
                description="The provided data is invalid (e.g., `content` field data empty).",
                response=inline_serializer(
                    name="MessageUpdateError",
                    fields={
                        "content": serializers.ListField(child=serializers.CharField())
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Invalid Content",
                        value={"content": ["This field may not be blank."]},
                    ),
                    OpenApiExample(
                        "Missing Content",
                        value={"content": ["This field is required."]},
                    ),
                    OpenApiExample(
                        "Invalid is_read",
                        value={"is_read": ["Must be a valid boolean."]},
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Message not found.",
                response=inline_serializer(
                    name="NotFoundError",
                    fields={
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "No Message matches the given query."},
                    )
                ],
            ),
        },
    )
    def patch(self, request, chat_room_id, pk, *args, **kwargs):
        """Update a message (partial update)"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)

        serializer = MessageSerializer(
            message,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="chat_room_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the chat room.",
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Unique identifier for the message.",
            ),
        ],
        responses={
            204: OpenApiResponse(
                description="Message deleted successfully. No content is returned."
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided.",
                response=inline_serializer(
                    name="UnauthorizedError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Message not found.",
                response=inline_serializer(
                    name="NotFoundError",
                    fields={
                        "detail": serializers.CharField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Not Found",
                        value={"detail": "No Message matches the given query."},
                    )
                ],
            ),
        },
    )
    def delete(self, request, chat_room_id, pk, *args, **kwargs):
        """Delete a message"""
        message = self.get_object(chat_room_id, pk)
        self.check_object_permissions(request, message)
        message.delete()
        return Response(
            {"message": "Message deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ChatRoomInvitationView(ChatAppBaseAPIView):
    """
    Handles sending, accepting, and declining chat room invitations.
    """

    def post(self, request, pk, action=None):
        if action is None:
            return self.send_invitation(request, pk)
        elif action == "accept":
            return self.accept_invitation(request, pk)
        elif action == "decline":
            return self.decline_invitation(request, pk)
        else:
            return Response(
                {"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
            )

    def send_invitation(self, request, pk):
        chat_room = get_object_or_404(ChatRoom, pk=pk)

        if not chat_room.can_manage(request.user):
            return Response(
                {"error": "You do not have permission to invite users to this room."},
                status=status.HTTP_403_FORBIDDEN,
            )
        invitee_id = request.data.get("invitee_id")

        if not invitee_id:
            return Response(
                {"error": "invitee_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.id == int(invitee_id):
            return Response(
                {"error": "You cannot invite yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if chat_room.participants.filter(id=invitee_id).exists():
            return Response(
                {"error": "User is already a participant."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_invite = ChatRoomInvitation.objects.filter(
            chat_room=chat_room, invitee_id=invitee_id, status="pending"
        ).first()

        if existing_invite:
            return Response(
                {"error": "A pending invitation already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation = ChatRoomInvitation.objects.create(
            chat_room=chat_room, invited_by=request.user, invitee_id=invitee_id
        )

        return Response(
            {"message": "Invitation sent.", "invitation_id": invitation.id},
            status=status.HTTP_201_CREATED,
        )

    def accept_invitation(self, request, pk):
        invitation = get_object_or_404(ChatRoomInvitation, pk=pk, invitee=request.user)

        if invitation.status != "pending":
            return Response(
                {"error": "This invitation is no longer pending."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = "accepted"
        invitation.save()
        invitation.chat_room.participants.add(request.user)

        return Response({"message": "Invitation accepted."})

    def decline_invitation(self, request, pk):
        invitation = get_object_or_404(ChatRoomInvitation, pk=pk, invitee=request.user)

        if invitation.status != "pending":
            return Response(
                {"error": "This invitation is no longer pending."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = "declined"
        invitation.save()

        return Response({"message": "Invitation declined."})
