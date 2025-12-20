"""API views for the slideshows app."""

import logging
from django.db import transaction
from rest_framework import generics, permissions
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)

from .models import Slideshow, Slide
from .serializers import (
    SlideshowListSerializer,
    SlideshowDetailSerializer,
    SlideSerializer,
)
from .permissions import IsOwnerOrReadOnly
from .pagination import SlideshowPagination

logger = logging.getLogger(__name__)


class SlideshowListCreateView(generics.ListCreateAPIView):
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

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SlideshowPagination

    def get_serializer_class(self):
        """Use list serializer for GET, detail serializer for POST."""
        if self.request.method == "POST":
            return SlideshowDetailSerializer
        return SlideshowListSerializer

    def get_queryset(self):
        """
        Return slideshows visible to the user.
        - User's own slideshows (all)
        - Public published slideshows from others
        """
        from django.db.models import Q

        user = self.request.user

        # Base queryset: user's own slideshows + public published ones
        queryset = Slideshow.objects.filter(
            Q(created_by=user) | Q(visibility="public", is_published=True)
        ).select_related("created_by")

        # Apply filters from query parameters
        visibility = self.request.query_params.get("visibility")
        if visibility:
            queryset = queryset.filter(visibility=visibility)

        subject = self.request.query_params.get("subject")
        if subject:
            queryset = queryset.filter(subject=subject)

        language = self.request.query_params.get("language")
        if language:
            queryset = queryset.filter(language=language)

        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(country=country)

        # Filter for only user's own slideshows
        mine_only = self.request.query_params.get("mine")
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
        return super().get(request, *args, **kwargs)

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
                            "notes": "Introduce yourself first",
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
        return super().post(request, *args, **kwargs)


class SlideshowRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
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

    queryset = Slideshow.objects.all().prefetch_related("slides")
    serializer_class = SlideshowDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

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
    def get(self, request, *args, **kwargs):
        """Get slideshow detail."""
        logger.debug(
            "Retrieving slideshow %s for user %s", kwargs.get("pk"), request.user
        )
        return super().get(request, *args, **kwargs)

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
    def patch(self, request, *args, **kwargs):
        """Update slideshow."""
        logger.info("Updating slideshow %s by user %s", kwargs.get("pk"), request.user)
        return super().patch(request, *args, **kwargs)

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
    def delete(self, request, *args, **kwargs):
        """Delete slideshow."""
        logger.info("Deleting slideshow %s by user %s", kwargs.get("pk"), request.user)
        return super().delete(request, *args, **kwargs)


class SlideCreateView(generics.CreateAPIView):
    """
    Create a new slide in an existing slideshow.

    POST: Create slide
          - Automatically associates with parent slideshow
          - Auto-assigns order if not specified (appends to end)
          - Increments slideshow version
          - Only the slideshow owner can create slides
    """

    serializer_class = SlideSerializer
    permission_classes = [permissions.IsAuthenticated]

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
                    "notes": "Spend extra time on decorators",
                },
            ),
            OpenApiExample(
                "Create slide with auto-order",
                value={
                    "content": "# Summary\n\nReview of key concepts",
                    "notes": "Leave time for Q&A",
                },
            ),
        ],
        tags=["Slideshows"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Create a new slide."""
        logger.info(
            "Creating slide for slideshow %s by user %s",
            kwargs.get("pk"),
            request.user,
        )
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Associate slide with slideshow and increment version."""
        from django.shortcuts import get_object_or_404
        from rest_framework.exceptions import PermissionDenied

        # Get parent slideshow from URL
        slideshow_id = self.kwargs.get("pk")
        slideshow = get_object_or_404(Slideshow, pk=slideshow_id)

        # Verify user is the owner of the slideshow
        if slideshow.created_by != self.request.user:
            raise PermissionDenied("Only the slideshow owner can add slides")

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


class SlideRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an individual slide.

    GET: Get slide detail (for caching and progressive loading)
    PATCH: Update slide content (owner only, increments version)
    DELETE: Delete slide (owner only, increments version)

    Same permission rules as parent slideshow apply.
    """

    queryset = Slide.objects.all().select_related("slideshow__created_by")
    serializer_class = SlideSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_url_kwarg = "slide_id"

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
    def get(self, request, *args, **kwargs):
        """Get individual slide."""
        logger.debug(
            "Retrieving slide %s for slideshow %s by user %s",
            kwargs.get("slide_id"),
            kwargs.get("pk"),
            request.user,
        )
        return super().get(request, *args, **kwargs)

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
    def patch(self, request, *args, **kwargs):
        """Update slide."""
        logger.info(
            "Updating slide %s by user %s", kwargs.get("slide_id"), request.user
        )
        return super().patch(request, *args, **kwargs)

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
    def delete(self, request, *args, **kwargs):
        """Delete slide."""
        logger.info(
            "Deleting slide %s by user %s", kwargs.get("slide_id"), request.user
        )
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Update slide and increment parent slideshow version."""
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

    def perform_destroy(self, instance):
        """Delete slide and increment parent slideshow version."""
        slideshow = instance.slideshow
        slide_id = instance.id

        # Delete the slide
        instance.delete()

        # Increment slideshow version
        slideshow.version += 1
        slideshow.save()

        logger.debug(
            "Slide %s deleted from slideshow %s (new version: %s)",
            slide_id,
            slideshow.id,
            slideshow.version,
        )
