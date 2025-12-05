import logging
from typing import Any, cast

from django.contrib.auth.models import AbstractBaseUser
from django.db import transaction
from rest_framework import exceptions, generics, permissions, serializers
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    inline_serializer,
)

from .models import CourseMembership
from .serializers import CourseSerializer

logger = logging.getLogger(__name__)


class CourseCreateView(generics.CreateAPIView):
    """Create a course for the authenticated user."""

    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create a course",
        description=(
            "Create a new course. Any authenticated user can create a course and the creator is "
            "automatically added to the course as a teacher membership."
        ),
        tags=["Courses"],
        request=CourseSerializer,
        responses={
            201: OpenApiResponse(
                description="Course successfully created.", response=CourseSerializer
            ),
            400: OpenApiResponse(
                description="Validation error.",
                response=inline_serializer(
                    name="CourseCreateValidationError",
                    fields={
                        "detail": serializers.CharField(required=False),
                        "title": serializers.ListField(
                            child=serializers.CharField(), required=False
                        ),
                        "end_date": serializers.ListField(
                            child=serializers.CharField(), required=False
                        ),
                    },
                ),
            ),
        },
        examples=[
            OpenApiExample(
                "Create course",
                summary="Successful creation",
                request_only=True,
                value={
                    "title": "Advanced Physics",
                    "outline": "Explore quantum mechanics and relativity.",
                    "language": "en",
                    "country": "US",
                    "subject": "physics",
                    "visibility": "private",
                    "start_date": "2024-09-01T08:00:00Z",
                    "end_date": "2024-12-15T20:00:00Z",
                    "allow_join_requests": True,
                },
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        logger.debug("Course creation requested by user %s", request.user)
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer: serializers.BaseSerializer[Any]) -> None:
        """Persist the course and link the creator as a teacher."""

        course_serializer = cast(CourseSerializer, serializer)
        course = course_serializer.save()
        request_user = self.request.user
        if not isinstance(request_user, AbstractBaseUser):
            raise exceptions.NotAuthenticated("Authentication is required to create a course.")
        if not request_user.is_authenticated:
            raise exceptions.NotAuthenticated("Authentication is required to create a course.")

        logger.info("Course %s (%s) created by %s", course.title, course.pk, self.request.user)
        CourseMembership.objects.create(
            course=course,
            user=request_user,
            role="teacher",
            status="enrolled",
        )
        logger.debug(
            "Teacher membership created for user %s in course %s", self.request.user, course.pk
        )
