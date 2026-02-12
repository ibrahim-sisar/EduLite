"""API views for the slideshows app."""

import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Slide, Slideshow
from .pagination import SlideshowPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    SlideSerializer,
    SlideshowDetailSerializer,
    SlideshowListSerializer,
)

logger = logging.getLogger(__name__)


class SlideshowsAppBaseAPIView(APIView):
    """Base API view for slideshows app."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """Include request context for serializers."""
        return {"request": self.request}


class SlideshowListCreateView(SlideshowsAppBaseAPIView):
    """
    List and create slideshows.

    GET: List slideshows visible to the user
         - User's own slideshows (any visibility)
         - Public published slideshows from other users
         - Supports filtering by ?visibility=, ?subject=, ?language=, ?mine=true
         - Paginated results (default 20 per page)

    POST: Create a new slideshow
          - Automatically sets created_by to the current user
          - Supports nested slide creation
    """

    def get_queryset(self, request):
        """
        Return slideshows visible to the user.
        - User's own slideshows (all)
        - Public published slideshows from others
        """
        from django.db.models import Q

        user = request.user

        # Base queryset: user's own slideshows + public published ones
        queryset = Slideshow.objects.filter(
            Q(created_by=user) | Q(visibility="public", is_published=True)
        ).select_related("created_by")

        # Apply filters from query parameters
        visibility = request.query_params.get("visibility")
        if visibility:
            queryset = queryset.filter(visibility=visibility)

        subject = request.query_params.get("subject")
        if subject:
            queryset = queryset.filter(subject=subject)

        language = request.query_params.get("language")
        if language:
            queryset = queryset.filter(language=language)

        country = request.query_params.get("country")
        if country:
            queryset = queryset.filter(country=country)

        # Filter for only user's own slideshows
        mine_only = request.query_params.get("mine")
        if mine_only and mine_only.lower() == "true":
            queryset = queryset.filter(created_by=user)

        return queryset.order_by("-updated_at")

    @extend_schema(
        summary="List slideshows",
        description=(
            "Returns slideshows visible to the user. "
            "Users see their own slideshows (any visibility) and public published slideshows from others. "
            "Supports filtering by visibility, subject, language, country. "
            "Results are paginated (default 20 per page, max 100)."
        ),
        parameters=[
            OpenApiParameter(
                "page",
                int,
                description="Page number for pagination",
                required=False,
            ),
            OpenApiParameter(
                "page_size",
                int,
                description="Number of results per page (default 20, max 100)",
                required=False,
            ),
            OpenApiParameter(
                "visibility",
                str,
                description="Filter by visibility (public, private, unlisted)",
                required=False,
            ),
            OpenApiParameter(
                "subject",
                str,
                description="Filter by subject",
                required=False,
            ),
            OpenApiParameter(
                "language",
                str,
                description="Filter by language",
                required=False,
            ),
            OpenApiParameter(
                "country",
                str,
                description="Filter by country",
                required=False,
            ),
            OpenApiParameter(
                "mine",
                bool,
                description="Show only user's own slideshows (true/false)",
                required=False,
            ),
        ],
        responses={
            200: SlideshowListSerializer(many=True),
        },
        tags=["Slideshows"],
    )
    def get(self, request, *args, **kwargs):
        """List slideshows."""
        logger.debug("Listing slideshows for user %s", request.user)

        queryset = self.get_queryset(request)

        paginator = SlideshowPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = SlideshowListSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create a slideshow",
        description=(
            "Create a new slideshow with optional slides. "
            "The created_by field is automatically set to the authenticated user. "
            "Slideshows can be public, private, or unlisted."
        ),
        request=SlideshowDetailSerializer,
        responses={
            201: SlideshowDetailSerializer,
        },
        examples=[
            OpenApiExample(
                "Create slideshow with slides",
                value={
                    "title": "Intro to Python",
                    "description": "Basics of Python programming",
                    "visibility": "private",
                    "subject": "computer_science",
                    "language": "en",
                    "is_published": False,
                    "slides": [
                        {
                            "order": 0,
                            "title": "Welcome",
                            "content": "# Welcome\n\nLet's learn Python!",
                        },
                        {
                            "order": 1,
                            "content": "# Variables\n\n{~ alert type='info' ~}\nVariables store data\n{~~}",
                        },
                    ],
                },
            ),
        ],
        tags=["Slideshows"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Create a slideshow."""
        logger.info(
            "Creating slideshow '%s' by user %s",
            request.data.get("title"),
            request.user,
        )
        serializer = SlideshowDetailSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SlideshowRetrieveUpdateDestroyView(SlideshowsAppBaseAPIView):
    """
    Retrieve, update, or delete a slideshow.

    GET: Get slideshow detail with slides
         - Supports ?initial=N to return only first N slides
         - Includes remaining_slide_ids for progressive loading
         - Users can view: their own slideshows, or public/unlisted published ones

    PATCH: Update slideshow (owner only)
           - Increments version number
           - Checks for version conflicts

    DELETE: Delete slideshow (owner only)
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, pk):
        """Retrieve slideshow or raise 404, with object-level permission check."""
        obj = get_object_or_404(Slideshow.objects.prefetch_related("slides"), pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        summary="Get slideshow detail",
        description=(
            "Returns detailed slideshow information including slides. "
            "Supports progressive loading via ?initial=N parameter to return only the first N slides. "
            "The remaining_slide_ids field contains IDs of slides not included in the response."
        ),
        parameters=[
            OpenApiParameter(
                "initial",
                int,
                description="Return only the first N slides (for progressive loading)",
                required=False,
            ),
        ],
        responses={
            200: SlideshowDetailSerializer,
            403: OpenApiResponse(description="Not authorized to view this slideshow"),
            404: OpenApiResponse(description="Slideshow not found"),
        },
        tags=["Slideshows"],
    )
    def get(self, request, pk, *args, **kwargs):
        """Get slideshow detail."""
        logger.debug("Retrieving slideshow %s for user %s", pk, request.user)
        slideshow = self.get_object(pk)
        serializer = SlideshowDetailSerializer(
            slideshow, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Update slideshow",
        description=(
            "Update slideshow metadata and/or slides. "
            "Only the owner can update slideshows. "
            "Version number is automatically incremented. "
            "Include the current version in request to detect conflicts."
        ),
        request=SlideshowDetailSerializer,
        responses={
            200: SlideshowDetailSerializer,
            403: OpenApiResponse(description="Not the slideshow owner"),
            409: OpenApiResponse(
                description="Version conflict",
                examples=[
                    OpenApiExample(
                        "Version conflict",
                        value={
                            "error": "version_conflict",
                            "message": "Slideshow was modified since you loaded it",
                            "server_version": 3,
                            "client_version": 2,
                        },
                    ),
                ],
            ),
        },
        tags=["Slideshows"],
    )
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """Update slideshow."""
        logger.info("Updating slideshow %s by user %s", pk, request.user)
        slideshow = self.get_object(pk)
        serializer = SlideshowDetailSerializer(
            slideshow,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        summary="Delete slideshow",
        description="Delete a slideshow. Only the owner can delete slideshows.",
        responses={
            204: OpenApiResponse(description="Slideshow deleted successfully"),
            403: OpenApiResponse(description="Not the slideshow owner"),
            404: OpenApiResponse(description="Slideshow not found"),
        },
        tags=["Slideshows"],
    )
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """Delete slideshow."""
        logger.info("Deleting slideshow %s by user %s", pk, request.user)
        slideshow = self.get_object(pk)
        slideshow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SlideCreateView(SlideshowsAppBaseAPIView):
    """
    Create a new slide in an existing slideshow.

    POST: Create slide
          - Automatically associates with parent slideshow
          - Auto-assigns order if not specified (appends to end)
          - Increments slideshow version
          - Only the slideshow owner can create slides
    """

    @extend_schema(
        summary="Create a new slide",
        description=(
            "Create a new slide in the specified slideshow. "
            "Only the slideshow owner can create slides. "
            "The slide is automatically associated with the parent slideshow. "
            "If order is not specified, it will be auto-assigned to append at the end. "
            "The parent slideshow's version number is incremented."
        ),
        request=SlideSerializer,
        responses={
            201: SlideSerializer,
            403: OpenApiResponse(description="Not the slideshow owner"),
            404: OpenApiResponse(description="Slideshow not found"),
        },
        examples=[
            OpenApiExample(
                "Create slide with explicit order",
                value={
                    "order": 3,
                    "title": "Advanced Topics",
                    "content": "# Advanced Python\n\nDecorators and more",
                },
            ),
            OpenApiExample(
                "Create slide with auto-order",
                value={
                    "content": "# Summary\n\nReview of key concepts",
                },
            ),
        ],
        tags=["Slideshows"],
    )
    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        """Create a new slide."""
        logger.info(
            "Creating slide for slideshow %s by user %s",
            pk,
            request.user,
        )

        # Get parent slideshow from URL
        slideshow = get_object_or_404(Slideshow, pk=pk)

        # Verify user is the owner of the slideshow
        if slideshow.created_by != request.user:
            raise PermissionDenied("Only the slideshow owner can add slides")

        serializer = SlideSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        # Save slide with slideshow relationship
        slide = serializer.save(slideshow=slideshow)

        # Increment slideshow version
        slideshow.version += 1
        slideshow.save()

        logger.debug(
            "Slide %s created in slideshow %s (new version: %s)",
            slide.id,
            slideshow.id,
            slideshow.version,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SlideRetrieveUpdateDestroyView(SlideshowsAppBaseAPIView):
    """
    Retrieve, update, or delete an individual slide.

    GET: Get slide detail (for caching and progressive loading)
    PATCH: Update slide content (owner only, increments version)
    DELETE: Delete slide (owner only, increments version)

    Same permission rules as parent slideshow apply.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, slide_id):
        """Retrieve slide or raise 404, with object-level permission check."""
        obj = get_object_or_404(
            Slide.objects.select_related("slideshow__created_by"), pk=slide_id
        )
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        summary="Get individual slide",
        description=(
            "Returns a single slide by ID. "
            "Used for background caching and progressive loading of large slideshows. "
            "Same permission rules as the parent slideshow apply."
        ),
        responses={
            200: SlideSerializer,
            403: OpenApiResponse(description="Not authorized to view this slide"),
            404: OpenApiResponse(description="Slide not found"),
        },
        tags=["Slideshows"],
    )
    def get(self, request, pk, slide_id, *args, **kwargs):
        """Get individual slide."""
        logger.debug(
            "Retrieving slide %s for slideshow %s by user %s",
            slide_id,
            pk,
            request.user,
        )
        slide = self.get_object(slide_id)
        serializer = SlideSerializer(slide, context=self.get_serializer_context())
        return Response(serializer.data)

    @extend_schema(
        summary="Update slide",
        description=(
            "Update an individual slide's content. "
            "Only the slideshow owner can update slides. "
            "The parent slideshow's version number is incremented. "
            "Markdown is automatically re-rendered on update."
        ),
        request=SlideSerializer,
        responses={
            200: SlideSerializer,
            403: OpenApiResponse(description="Not the slideshow owner"),
            404: OpenApiResponse(description="Slide not found"),
        },
        tags=["Slideshows"],
    )
    @transaction.atomic
    def patch(self, request, pk, slide_id, *args, **kwargs):
        """Update slide."""
        logger.info("Updating slide %s by user %s", slide_id, request.user)
        slide = self.get_object(slide_id)
        serializer = SlideSerializer(
            slide,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        slide = serializer.save()

        # Increment parent slideshow version
        slideshow = slide.slideshow
        slideshow.version += 1
        slideshow.save()

        logger.debug(
            "Slide %s updated in slideshow %s (new version: %s)",
            slide.id,
            slideshow.id,
            slideshow.version,
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Delete slide",
        description=(
            "Delete an individual slide. "
            "Only the slideshow owner can delete slides. "
            "The parent slideshow's version number is incremented."
        ),
        responses={
            204: OpenApiResponse(description="Slide deleted successfully"),
            403: OpenApiResponse(description="Not the slideshow owner"),
            404: OpenApiResponse(description="Slide not found"),
        },
        tags=["Slideshows"],
    )
    @transaction.atomic
    def delete(self, request, pk, slide_id, *args, **kwargs):
        """Delete slide."""
        logger.info("Deleting slide %s by user %s", slide_id, request.user)
        slide = self.get_object(slide_id)
        slideshow = slide.slideshow
        slide_id_val = slide.id

        # Delete the slide
        slide.delete()

        # Increment slideshow version
        slideshow.version += 1
        slideshow.save()

        logger.debug(
            "Slide %s deleted from slideshow %s (new version: %s)",
            slide_id_val,
            slideshow.id,
            slideshow.version,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========== Search Endpoint ==========


@extend_schema(tags=["Slideshows"])
class SlideshowSearchView(SlideshowsAppBaseAPIView):
    """
    Search slideshows by title or description.

    GET: Returns paginated search results.
         - Text search across title and description (case-insensitive)
         - Minimum query length: 2 characters
         - Visibility rules: user sees own slideshows (any visibility) + public published from others
         - Supports combining search with filters (visibility, subject, language, country, mine)
    """

    @extend_schema(
        summary="Search slideshows",
        description=(
            "Search for slideshows by title or description. "
            "Returns slideshows visible to the user: their own (any visibility) "
            "and public published slideshows from others. "
            "Supports combining text search with filters."
        ),
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Search query (minimum 2 characters)",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
                required=False,
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page (default 20, max 100)",
                required=False,
            ),
            OpenApiParameter(
                name="visibility",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by visibility (public, private, unlisted)",
                required=False,
            ),
            OpenApiParameter(
                name="subject",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by subject",
                required=False,
            ),
            OpenApiParameter(
                name="language",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by language",
                required=False,
            ),
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by country",
                required=False,
            ),
            OpenApiParameter(
                name="mine",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Show only user's own slideshows (true/false)",
                required=False,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Search results",
                response=inline_serializer(
                    name="SlideshowSearchPaginatedResponse",
                    fields={
                        "count": serializers.IntegerField(),
                        "next": serializers.URLField(allow_null=True),
                        "previous": serializers.URLField(allow_null=True),
                        "total_pages": serializers.IntegerField(),
                        "current_page": serializers.IntegerField(),
                        "page_size": serializers.IntegerField(),
                        "results": SlideshowListSerializer(many=True),
                    },
                ),
            ),
            400: OpenApiResponse(
                description="Invalid search query",
                response=inline_serializer(
                    name="SlideshowSearchError",
                    fields={"detail": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Query Too Short",
                        value={
                            "detail": "Search query must be at least 2 characters long."
                        },
                    ),
                ],
            ),
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    def get(self, request, *args, **kwargs):
        from .logic.slideshow_search_logic import (
            apply_slideshow_filters,
            build_slideshow_search_queryset,
            validate_search_query,
        )

        search_query = request.query_params.get("q", "").strip()

        # Step 1: Validate query
        is_valid, error_response = validate_search_query(search_query)
        if not is_valid:
            return error_response

        # Step 2: Build search queryset with visibility rules
        queryset = build_slideshow_search_queryset(search_query, request.user)

        # Step 3: Apply optional filters
        queryset = apply_slideshow_filters(queryset, request.query_params, request.user)

        # Step 4: Paginate
        paginator = SlideshowPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        # Step 5: Serialize and return
        serializer = SlideshowListSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return paginator.get_paginated_response(serializer.data)


# ========== Preview Endpoint ==========

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle


class PreviewThrottle(UserRateThrottle):
    """Throttle preview requests - 30 per minute (~1 every 2 seconds)"""

    rate = "30/min"


@extend_schema(
    summary="Preview markdown rendering",
    description="Renders markdown to HTML without saving. Used for live preview in editor.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Markdown content to render",
                    "example": "# Hello\n\nThis is **bold** text.",
                }
            },
            "required": ["content"],
        }
    },
    responses={
        200: OpenApiResponse(
            description="Successfully rendered markdown",
            response={
                "type": "object",
                "properties": {
                    "rendered_content": {
                        "type": "string",
                        "description": "Rendered HTML",
                    }
                },
            },
        ),
        400: OpenApiResponse(description="Invalid markdown or rendering error"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([PreviewThrottle])
def preview_markdown(request):
    """
    Preview markdown rendering without saving to database.

    POST /api/slideshows/preview/
    Body: {"content": "# Markdown"}
    Returns: {"rendered_content": "<h1>Markdown</h1>"}

    Throttled to 30 requests per minute per user.
    """
    content = request.data.get("content", "")

    if not content:
        return Response({"rendered_content": ""}, status=status.HTTP_200_OK)

    try:
        from django_spellbook.parsers import spellbook_render

        rendered = spellbook_render(content)

        logger.debug(
            "Preview rendered for user %s (%d chars -> %d chars)",
            request.user.username,
            len(content),
            len(rendered),
        )

        return Response({"rendered_content": rendered}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Preview render error for user {request.user.username}: {e}")
        return Response(
            {"error": "Failed to render markdown", "detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
