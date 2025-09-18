from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase
from ...models import FriendSuggestion


class FriendSuggestionListViewTest(UsersAppTestCase):
    """Tests for the FriendSuggestionListView API endpoint."""

    def setUp(self):
        super().setUp()
        self.url = reverse("friend-suggestion-list")

        # Create friend suggestions for Ahmad
        FriendSuggestion.objects.create(
            user=self.ahmad,
            suggested_user=self.miguel,
            score=0.9,
            reason="3 mutual friends",
        )
        FriendSuggestion.objects.create(
            user=self.ahmad,
            suggested_user=self.fatima,
            score=0.5,
            reason="Same course",
        )

    def test_requires_authentication(self):
        """Endpoint should require authentication."""
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_returns_suggestions_ordered_by_score(self):
        """Suggestions are returned ordered by descending score."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
        scores = [s["score"] for s in response.data]
        self.assertGreaterEqual(scores[0], scores[1])
        self.assertEqual(response.data[0]["suggested_user"]["id"], self.miguel.id)

    def test_filter_by_reason(self):
        """Can filter suggestions by reason case-insensitively."""
        self.authenticate_as(self.ahmad)
        response = self.client.get(self.url, {"type": "3 MUTUAL FRIENDS"})
        self.assert_response_success(response, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["suggested_user"]["id"], self.miguel.id)
