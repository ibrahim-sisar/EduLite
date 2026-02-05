import logging

from chat.models import Message as ChatRoomMessage
from django.db.models import Q

from users.models import FriendSuggestion, User
from users.services import UserQueryService

logger = logging.getLogger(__name__)


def compute_friend_suggestions_for_user(user):
    logger.info("Computing friend suggestions for user %s", user.pk)

    candidates = User.objects.exclude(
        Q(id=user.id)
        | Q(id__in=user.profile.friends.values_list("id", flat=True))
        | Q(
            id__in=user.profile.sent_friend_requests.values_list(
                "receiver_id", flat=True
            )
        )
        | Q(
            id__in=user.profile.received_friend_requests.values_list(
                "sender_id", flat=True
            )
        )
    )

    total_candidates = candidates.count()
    logger.debug("Total candidates after exclusion: %d", total_candidates)

    # Pre-compute user's courses, teachers, and chatrooms for efficiency
    user_course_ids = UserQueryService.get_user_course_ids(user)
    user_teacher_ids = UserQueryService.get_user_teacher_ids(user)
    user_chatroom_ids = UserQueryService.get_user_chatroom_ids(user)

    scored_candidates = []

    for candidate in candidates:
        score: float = 0
        reasons = []

        # Mutual friends
        mutual_friends = set(user.profile.friends.all()) & set(
            candidate.profile.friends.all()
        )
        mutual_count = len(mutual_friends)
        if mutual_count:
            score += mutual_count
            reasons.append(f"{mutual_count} mutual friends")
        logger.debug(
            "Candidate %s - Mutual friends count: %d", candidate.pk, mutual_count
        )

        # Same course
        candidate_course_ids = UserQueryService.get_user_course_ids(candidate)
        shared_courses = user_course_ids & candidate_course_ids
        if shared_courses:
            score += 1
            reasons.append("Same course")
        logger.debug(
            "Candidate %s - Shared courses: %s", candidate.pk, list(shared_courses)
        )

        # Same teacher
        candidate_teacher_ids = UserQueryService.get_user_teacher_ids(candidate)
        shared_teachers = user_teacher_ids & candidate_teacher_ids
        if shared_teachers:
            score += 1
            reasons.append("Same teacher")
        logger.debug(
            "Candidate %s - Shared teachers count: %d",
            candidate.pk,
            len(shared_teachers),
        )

        # Recent chatroom activity
        chat_active = ChatRoomMessage.objects.filter(
            chat_room_id__in=user_chatroom_ids, sender=candidate
        ).exists()
        if chat_active:
            score += 0.5
            reasons.append("Recently messaged in shared chatroom")
        logger.debug("Candidate %s - Chat activity: %s", candidate.pk, chat_active)

        if score > 0:
            scored_candidates.append((candidate, score, reasons[0]))  # pick top reason
            logger.debug(
                "Candidate %s computed with total score %.1f and primary reason '%s'",
                candidate.pk,
                score,
                reasons[0],
            )

    logger.info(
        "Storing friend suggestions for user %s. Total suggestions computed: %d",
        user.pk,
        len(scored_candidates),
    )

    # Remove existing suggestions
    FriendSuggestion.objects.filter(user=user).delete()

    # Create new suggestions
    created_suggestions = FriendSuggestion.objects.bulk_create(
        [
            FriendSuggestion(user=user, suggested_user=cand, score=score, reason=reason)
            for cand, score, reason in scored_candidates
        ]
    )
    logger.info(
        "Stored %d friend suggestion(s) for user %s", len(created_suggestions), user.pk
    )
