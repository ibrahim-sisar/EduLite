from django.urls import reverse
from django.test import TestCase
from django.db.models.signals import post_save
from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth import get_user_model
from chat.models import ChatRoom, ChatRoomInvitation
from notifications.models import Notification
from chat.signals import notify_user_on_invitation

User = get_user_model()


class ChatRoomInvitationTests(APITestCase):
    def setUp(self):
        # Users
        self.creator = User.objects.create_user(username="creator", password="pass1234")
        self.editor = User.objects.create_user(username="editor", password="pass1234")
        self.invitee = User.objects.create_user(username="invitee", password="pass1234")
        self.other = User.objects.create_user(username="other", password="pass1234")

        # Room
        self.room = ChatRoom.objects.create(
            name="Room A", room_type="GROUP", creator=self.creator
        )
        self.room.participants.add(self.creator)
        self.room.participants.add(self.editor)
        self.room.editors.add(self.editor)

        self.invite_url = reverse("chatroom-invite", kwargs={"pk": self.room.pk})

    def _accept_url(self, invitation):
        return reverse("chatroom-invite-accept", kwargs={"pk": invitation.pk})

    def _decline_url(self, invitation):
        return reverse("chatroom-invite-decline", kwargs={"pk": invitation.pk})

    def test_creator_can_send_invitation_and_notification_created(self):
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(
            self.invite_url, {"invitee_id": self.invitee.id}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ChatRoomInvitation.objects.filter(
                chat_room=self.room, invitee=self.invitee, status="pending"
            ).exists()
        )
        # Expect a notification to be created by the post_save signal
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.invitee, actor=self.creator, verb__icontains="invited"
            ).exists()
        )

    def test_editor_can_send_invitation(self):
        self.client.force_authenticate(user=self.editor)
        resp = self.client.post(
            self.invite_url, {"invitee_id": self.invitee.id}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_non_manager_cannot_send_invitation(self):
        # A user who is not creator/editor should not be able to invite
        self.client.force_authenticate(user=self.other)
        resp = self.client.post(
            self.invite_url, {"invitee_id": self.invitee.id}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_invite_self(self):
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(
            self.invite_url, {"invitee_id": self.creator.id}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You cannot invite yourself", str(resp.data))

    def test_cannot_invite_existing_participant(self):
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(
            self.invite_url, {"invitee_id": self.editor.id}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already a participant", str(resp.data))

    def test_duplicate_pending_invitation_rejected(self):
        self.client.force_authenticate(user=self.creator)
        first = self.client.post(
            self.invite_url, {"invitee_id": self.invitee.id}, format="json"
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(
            self.invite_url, {"invitee_id": self.invitee.id}, format="json"
        )
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pending invitation", str(second.data))

    def test_accept_invitation_adds_participant(self):
        # Temporarily disconnect signal to avoid side-effects when creating an invitation directly
        post_save.disconnect(
            receiver=notify_user_on_invitation, sender=ChatRoomInvitation
        )
        try:
            inv = ChatRoomInvitation.objects.create(
                chat_room=self.room,
                invited_by=self.creator,
                invitee=self.invitee,
                status="pending",
            )
        finally:
            post_save.connect(
                receiver=notify_user_on_invitation, sender=ChatRoomInvitation
            )

        self.client.force_authenticate(user=self.invitee)
        resp = self.client.post(self._accept_url(inv))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        inv.refresh_from_db()
        self.assertEqual(inv.status, "accepted")
        self.assertTrue(self.room.participants.filter(id=self.invitee.id).exists())

    def test_decline_invitation(self):
        post_save.disconnect(
            receiver=notify_user_on_invitation, sender=ChatRoomInvitation
        )
        try:
            inv = ChatRoomInvitation.objects.create(
                chat_room=self.room,
                invited_by=self.creator,
                invitee=self.invitee,
                status="pending",
            )
        finally:
            post_save.connect(
                receiver=notify_user_on_invitation, sender=ChatRoomInvitation
            )

        self.client.force_authenticate(user=self.invitee)
        resp = self.client.post(self._decline_url(inv))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        inv.refresh_from_db()
        self.assertEqual(inv.status, "declined")
        self.assertFalse(self.room.participants.filter(id=self.invitee.id).exists())

    def test_accept_or_decline_only_when_pending(self):
        post_save.disconnect(
            receiver=notify_user_on_invitation, sender=ChatRoomInvitation
        )
        try:
            inv = ChatRoomInvitation.objects.create(
                chat_room=self.room,
                invited_by=self.creator,
                invitee=self.invitee,
                status="accepted",
            )
        finally:
            post_save.connect(
                receiver=notify_user_on_invitation, sender=ChatRoomInvitation
            )

        self.client.force_authenticate(user=self.invitee)
        # Accept should fail
        resp_accept = self.client.post(self._accept_url(inv))
        self.assertEqual(resp_accept.status_code, status.HTTP_400_BAD_REQUEST)
        # Decline should fail
        resp_decline = self.client.post(self._decline_url(inv))
        self.assertEqual(resp_decline.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_invitee_id_returns_400(self):
        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.invite_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
