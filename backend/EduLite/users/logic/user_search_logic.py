# backend/EduLite/users/logic/user_search_logic.py
# Contains logic functions for user search functionality with privacy controls

from typing import Optional, Tuple, Any
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q, Exists, OuterRef
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

User = get_user_model()


def validate_search_query(search_query: str, min_length: int = 2) -> Tuple[bool, Optional[Response]]:
    """
    Validates the search query parameters.

    Args:
        search_query: The search query string to validate
        min_length: Minimum required length for the search query

    Returns:
        Tuple of (is_valid, error_response_or_none)
        - If valid: (True, None)
        - If invalid: (False, Response with error details)
    """
    if not search_query or not search_query.strip():
        return False, Response(
            {"detail": "Search query is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    search_query = search_query.strip()

    if len(search_query) < min_length:
        return False, Response(
            {"detail": f"Search query must be at least {min_length} characters long."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return True, None


def build_privacy_aware_search_queryset(search_query: str, requesting_user: Optional[User]) -> QuerySet:
    """
    Creates a privacy-aware search queryset that only searches fields the requesting user can see.

    Args:
        search_query: The validated search query string
        requesting_user: The user performing the search

    Returns:
        QuerySet of User objects matching the search criteria with privacy respected
    """
    search_query = search_query.strip()

    # Start with all users, selecting related profile and privacy settings for efficiency
    queryset = User.objects.select_related('profile', 'profile__privacy_settings')

    # Build search conditions based on what fields the requesting user can see
    search_conditions = Q()

    # Username is always searchable (it's the public identifier)
    search_conditions |= Q(username__icontains=search_query)

    # Build conditions for users whose names can be searched
    name_searchable_conditions = Q()

    # Only search by name if the requesting user can see names
    if requesting_user and requesting_user.is_authenticated:

        # Can always search own name
        name_searchable_conditions |= Q(id=requesting_user.id)

        # Can search names of users who show full name to this requesting user
        # This follows the same logic as UserSerializer._should_show_full_name

    # Users with show_full_name=True (visible to authenticated users)
    name_searchable_conditions |= Q(profile__privacy_settings__show_full_name=True)

    # Apply name search only to users whose names are visible
    name_search = Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
    search_conditions |= (name_searchable_conditions & name_search)

    # Apply the combined search conditions
    return queryset.filter(search_conditions).distinct().order_by("username")


def build_base_search_queryset(search_query: str, requesting_user: Optional[User] = None) -> QuerySet:
    """
    Creates the base search queryset with privacy-aware field searching.

    Args:
        search_query: The validated search query string
        requesting_user: The user performing the search (for privacy-aware searching)

    Returns:
        QuerySet of User objects matching the search criteria
    """
    # Use the new privacy-aware search logic
    return build_privacy_aware_search_queryset(search_query, requesting_user)


def apply_privacy_filters(queryset: QuerySet, requesting_user: Optional[User]) -> QuerySet:
    """
    Applies privacy settings to filter out users based on their privacy preferences
    and the requesting user's relationship to them.

    Uses database-level filtering for better performance.

    Args:
        queryset: The base search queryset to filter
        requesting_user: The user performing the search (can be None for anonymous users)

    Returns:
        QuerySet filtered according to privacy settings
    """
    if not requesting_user or not requesting_user.is_authenticated:
        # Anonymous users can only see users with 'everyone' search visibility
        return queryset.filter(
            profile__privacy_settings__search_visibility='everyone'
        )

    # For authenticated users, build complex filter conditions
    # Users visible to requesting user if:
    # 1. They are the same user (can always find themselves)
    # 2. search_visibility is 'everyone'
    # 3. search_visibility is 'friends_only' AND requesting_user is in their friends
    # 4. search_visibility is 'friends_of_friends' AND they share mutual friends or are direct friends

    # Self visibility
    self_filter = Q(id=requesting_user.id)

    # Everyone visibility
    everyone_filter = Q(profile__privacy_settings__search_visibility='everyone')

    # Friends only visibility
    friends_only_filter = Q(
        profile__privacy_settings__search_visibility='friends_only',
        profile__friends=requesting_user
    )

    # Friends of friends visibility - more complex query
    # Check if requesting user is a direct friend
    direct_friend_filter = Q(profile__friends=requesting_user)

    # Check for mutual friends using Exists subquery
    mutual_friends_subquery = User.objects.filter(
        friend_profiles=OuterRef('id'),  # Users who are friends with the target user
        id__in=requesting_user.friend_profiles.values_list('id', flat=True)  # Who are also friends with requesting user
    )

    friends_of_friends_filter = Q(
        profile__privacy_settings__search_visibility='friends_of_friends'
    ) & (direct_friend_filter | Exists(mutual_friends_subquery))

    # Combine all conditions with OR
    final_filter = self_filter | everyone_filter | friends_only_filter | friends_of_friends_filter

    return queryset.filter(final_filter)


def paginate_search_results(
    queryset: QuerySet,
    request: HttpRequest,
    view_instance,
    page_size: int = 10
) -> Tuple[QuerySet, Optional[PageNumberPagination]]:
    """
    Handles pagination of search results.

    Args:
        queryset: The filtered queryset to paginate
        request: The HTTP request object
        view_instance: The view instance for pagination context
        page_size: Number of results per page

    Returns:
        Tuple of (queryset, paginator_instance_or_none)
        - If paginated: (original_queryset, paginator_with_page_set)
        - If not paginated: (queryset, None)
    """
    paginator = PageNumberPagination()
    paginator.page_size = page_size

    # Ensure we have a DRF Request object for pagination compatibility
    if not hasattr(request, 'query_params'):
        # Wrap Django HttpRequest in DRF Request
        drf_request = Request(request)
    else:
        drf_request = request

    page = paginator.paginate_queryset(queryset, drf_request, view=view_instance)

    if page is not None:
        # Return original queryset and the paginator instance with page set
        # The paginator now contains the page data internally
        return queryset, paginator

    # Return the full queryset for non-paginated response
    return queryset, None


def execute_user_search(
    search_query: str,
    requesting_user: Optional[User],
    request: HttpRequest,
    view_instance,
    min_query_length: int = 2,
    page_size: int = 10,
    bypass_privacy_filters: bool = False
) -> Tuple[bool, Optional[QuerySet], Optional[PageNumberPagination], Optional[Response]]:
    """Main function that orchestrates the user search process with privacy controls."""

    # Step 1: Validate search query
    is_valid, error_response = validate_search_query(search_query, min_query_length)
    if not is_valid:
        return False, None, None, error_response

    # Step 2: Build privacy-aware search queryset
    if bypass_privacy_filters:
        # Admin search - use old logic that searches all fields
        base_queryset = User.objects.select_related('profile', 'profile__privacy_settings').filter(
            Q(username__icontains=search_query.strip()) |
            Q(first_name__icontains=search_query.strip()) |
            Q(last_name__icontains=search_query.strip())
        ).distinct().order_by("username")
    else:
        # Regular search - respect privacy settings
        base_queryset = build_base_search_queryset(search_query, requesting_user)

    if not bypass_privacy_filters:
        # Step 3: Apply visibility privacy filters
        final_queryset = apply_privacy_filters(base_queryset, requesting_user)
    else:
        final_queryset = base_queryset

    # Step 4: Handle pagination
    page_or_queryset, paginator = paginate_search_results(
        final_queryset, request, view_instance, page_size
    )

    return True, page_or_queryset, paginator, None


def filter_user_display_data(users_queryset: QuerySet, requesting_user: Optional[User]) -> QuerySet:
    """
    Additional filtering to respect privacy settings for what user data is displayed
    in search results (e.g., showing/hiding full names based on privacy settings).

    This function doesn't filter out users, but can be used to modify what data
    is shown for each user in the serializer context.

    Args:
        users_queryset: The privacy-filtered queryset
        requesting_user: The user performing the search

    Returns:
        The same queryset (this function is for future extensibility)
    """
    # For now, return the queryset as-is
    # This function provides a hook for future enhancements like:
    # - Hiding full names based on show_full_name setting
    # - Hiding email addresses based on show_email setting
    # - Showing different profile picture visibility levels

    return users_queryset


def get_user_friends_ids(user: User) -> set:
    """
    Get a set of user IDs that are friends with the given user.

    Args:
        user: The user to get friends for

    Returns:
        Set of user IDs that are friends with the given user
    """
    if not user or not user.is_authenticated:
        return set()

    try:
        return set(user.friend_profiles.values_list('id', flat=True))
    except AttributeError:
        return set()


def have_mutual_friends(user1: User, user2: User) -> bool:
    """
    Check if two users have mutual friends.

    Args:
        user1: First user
        user2: Second user

    Returns:
        True if users have mutual friends, False otherwise
    """
    if not user1 or not user2 or not user1.is_authenticated or not user2.is_authenticated:
        return False

    # Same user cannot have mutual friends with themselves
    if user1.id == user2.id:
        return False

    user1_friends = get_user_friends_ids(user1)
    user2_friends = get_user_friends_ids(user2)

    # Check if there's any intersection between friend lists
    return bool(user1_friends.intersection(user2_friends))
