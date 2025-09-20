from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from users.logic.friend_suggestions import compute_friend_suggestions_for_user
from users.models import FriendSuggestion
from chat.models import Message as ChatRoomMessage, ChatRoom
from courses.models import Course, CourseMembership

User = get_user_model()


class FriendSuggestionsTests(TestCase):
    def setUp(self):
        """
        Create users and clear any preexisting suggestions.
        Set up dummy m2m relations by assuming that the User model
        has friends, courses, teachers, and chatrooms m2m relations.
        """
        self.user_target = User.objects.create_user(username="target", password="pass")
        self.user_candidate = User.objects.create_user(
            username="user_candidate", password="pass"
        )
        self.user_common = User.objects.create_user(username="common", password="pass")
        self.teacher = User.objects.create_user(username="teacher", password="pass")

        self.course101 = Course.objects.create(title="course101")
        self.course102 = Course.objects.create(title="course102")

        self.chatroom = ChatRoom.objects.create(room_type="GROUP")

        # Clear any friend suggestions for the target user
        FriendSuggestion.objects.filter(user=self.user_target).delete()

    def test_mutual_friends_suggestion(self):
        """
        Test that a candidate who shares mutual friend(s) gets a suggestion,
        and that the score and reason reflect the mutual friends count.
        """
        # Set up mutual friend relation:
        # target and candidate both are friends with common user.
        self.user_target.profile.friends.add(self.user_common)
        self.user_candidate.profile.friends.add(self.user_common)

        compute_friend_suggestions_for_user(self.user_target)
        suggestion = FriendSuggestion.objects.filter(
            user=self.user_target, suggested_user=self.user_candidate
        ).first()
        self.assertIsNotNone(suggestion)
        # Expect score to equal the number of mutual friends (1 in this case)
        self.assertEqual(suggestion.score, 1)
        self.assertEqual(suggestion.reason, "1 mutual friends")

    def test_same_course_suggestion(self):
        """
        Test that when users share the same course (and nothing else), a suggestion is created.
        """
        CourseMembership.objects.create(
            user=self.user_target, course=self.course101, role="student"
        )
        CourseMembership.objects.create(
            user=self.user_candidate, course=self.course101, role="student"
        )

        compute_friend_suggestions_for_user(self.user_target)
        suggestion = FriendSuggestion.objects.filter(
            user=self.user_target, suggested_user=self.user_candidate
        ).first()
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.score, 1)
        self.assertEqual(suggestion.reason, "Same course")

    def test_same_teacher_suggestion(self):
        """
        Test that when users share the same teacher, a suggestion is created.
        """
        CourseMembership.objects.create(
            user=self.user_target, course=self.course101, role="student"
        )
        CourseMembership.objects.create(
            user=self.teacher, course=self.course101, role="teacher"
        )

        CourseMembership.objects.create(
            user=self.user_candidate, course=self.course102, role="student"
        )
        CourseMembership.objects.create(
            user=self.teacher, course=self.course102, role="teacher"
        )

        compute_friend_suggestions_for_user(self.user_target)
        suggestion = FriendSuggestion.objects.filter(
            user=self.user_target, suggested_user=self.user_candidate
        ).first()
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.score, 1)
        self.assertEqual(suggestion.reason, "Same teacher")

    def test_recent_chatroom_message(self):
        """
        Test that a suggestion is created when the candidate has recently messaged
        in a chatroom shared with the target user.
        """
        self.chatroom.participants.add(self.user_target)

        # Create a chat message from user2 in the shared chatroom.
        ChatRoomMessage.objects.create(
            chat_room=self.chatroom, sender=self.user_candidate, content="Hi there!"
        )

        # Run friend suggestion computation.
        compute_friend_suggestions_for_user(self.user_target)

        # Retrieve and verify the created friend suggestion.
        suggestion = FriendSuggestion.objects.get(
            user=self.user_target, suggested_user=self.user_candidate
        )
        self.assertEqual(suggestion.score, 0.5)
        self.assertEqual(suggestion.reason, "Recently messaged in shared chatroom")

    def test_no_suggestion_without_common_factors(self):
        """
        Test that no suggestion is created when candidate does not share any criteria
        with the target user.
        """
        compute_friend_suggestions_for_user(self.user_target)
        suggestion = FriendSuggestion.objects.filter(
            user=self.user_target, suggested_user=self.user_candidate
        ).first()
        self.assertIsNone(suggestion)

    def test_existing_suggestions_are_cleared(self):
        """
        Test that previous friend suggestions for a user are removed before creating new ones.
        """
        # Create an existing suggestion.
        FriendSuggestion.objects.create(
            user=self.user_target,
            suggested_user=self.user_candidate,
            score=5,
            reason="Old suggestion",
        )
        self.assertEqual(
            FriendSuggestion.objects.filter(user=self.user_target).count(), 1
        )

        # Establish a mutual friend relationship to cause a fresh suggestion.
        self.user_target.profile.friends.add(self.user_common)
        self.user_candidate.profile.friends.add(self.user_common)

        compute_friend_suggestions_for_user(self.user_target)
        suggestions = FriendSuggestion.objects.filter(
            user=self.user_target, suggested_user=self.user_candidate
        )
        self.assertEqual(suggestions.count(), 1)
        suggestion = suggestions.first()
        self.assertEqual(suggestion.score, 1)
        self.assertEqual(suggestion.reason, "1 mutual friends")
