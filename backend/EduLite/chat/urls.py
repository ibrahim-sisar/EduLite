from django.urls import path
from . import views

urlpatterns = [
    # chat urls
    path("rooms/", views.ChatRoomListCreateView.as_view(), name="chat-room-list"),
    path(
        "rooms/<int:pk>/", views.ChatRoomDetailView.as_view(), name="chat-room-detail"
    ),
    # messages urls
    path(
        "rooms/<int:chat_room_id>/messages/",
        views.MessageListCreateView.as_view(),
        name="message-list-create",
    ),
    path(
        "rooms/<int:chat_room_id>/messages/<int:pk>/",
        views.MessageDetailView.as_view(),
        name="message-detail",
    ),
    # Send invitation
    path(
        "rooms/<int:pk>/invite/",
        views.ChatRoomInvitationView.as_view(),
        name="chatroom-invite",
    ),
    # Accept/Decline invitation
    path(
        "invitations/<int:pk>/accept/",
        views.ChatRoomInvitationView.as_view(),
        {"action": "accept"},
        name="chatroom-invite-accept",
    ),
    path(
        "invitations/<int:pk>/decline/",
        views.ChatRoomInvitationView.as_view(),
        {"action": "decline"},
        name="chatroom-invite-decline",
    ),
]
