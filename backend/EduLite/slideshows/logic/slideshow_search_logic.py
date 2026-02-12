"""Business logic for slideshow search functionality."""

from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()


def validate_search_query(
    search_query: str, min_length: int = 2
) -> Tuple[bool, Optional[Response]]:
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


def build_slideshow_search_queryset(
    search_query: str,
    user,
) -> QuerySet:
    """
    Creates a search queryset that respects slideshow visibility rules.

    Users see:
    - Their own slideshows (any visibility, any published state)
    - Public published slideshows from other users

    Args:
        search_query: The validated search query string
        user: The authenticated user performing the search

    Returns:
        QuerySet of Slideshow objects matching the search criteria
    """
    from slideshows.models import Slideshow

    search_query = search_query.strip()

    # Visibility: own slideshows + public published from others
    visibility_filter = Q(created_by=user) | Q(visibility="public", is_published=True)

    # Text search across title and description
    text_filter = Q(title__icontains=search_query) | Q(
        description__icontains=search_query
    )

    queryset = (
        Slideshow.objects.filter(visibility_filter & text_filter)
        .select_related("created_by")
        .order_by("-updated_at")
    )

    return queryset


def apply_slideshow_filters(queryset: QuerySet, params: dict, user) -> QuerySet:
    """
    Applies optional filters from query parameters to the search queryset.

    Args:
        queryset: The base search queryset to filter
        params: Query parameters dict (from request.query_params)
        user: The authenticated user (for 'mine' filter)

    Returns:
        Filtered QuerySet
    """
    visibility = params.get("visibility")
    if visibility:
        queryset = queryset.filter(visibility=visibility)

    subject = params.get("subject")
    if subject:
        queryset = queryset.filter(subject=subject)

    language = params.get("language")
    if language:
        queryset = queryset.filter(language=language)

    country = params.get("country")
    if country:
        queryset = queryset.filter(country=country)

    mine_only = params.get("mine")
    if mine_only and mine_only.lower() == "true":
        queryset = queryset.filter(created_by=user)

    return queryset
