# python
from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from users.models import FriendSuggestion

User = get_user_model()


class FriendSuggestionModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="user1", password="password123")
        cls.user2 = User.objects.create_user(username="user2", password="password123")

    def test_create_friend_suggestion(self):
        """
        Test that a FriendSuggestion instance is created successfully.
        """
        suggestion = FriendSuggestion.objects.create(
            user=self.user1,
            suggested_user=self.user2,
            score=0.85,
            reason="2 mutual friends",
        )
        self.assertIsNotNone(suggestion.pk)
        self.assertIsNotNone(suggestion.created_at)
        self.assertEqual(suggestion.score, 0.85)

    def test_unique_friend_suggestion_constraint(self):
        """
        Test the unique_together constraint for (user, suggested_user).
        """
        FriendSuggestion.objects.create(
            user=self.user1,
            suggested_user=self.user2,
            score=0.90,
            reason="Similar interests",
        )
        with self.assertRaises(IntegrityError):
            FriendSuggestion.objects.create(
                user=self.user1,
                suggested_user=self.user2,
                score=0.92,
                reason="Duplicate suggestion",
            )
