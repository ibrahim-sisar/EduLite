import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import exceptions, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, CourseMembership, CourseModule
from .permissions import CanCreateCourse, IsCourseMember, IsCourseTeacher
from .serializers import CourseModuleSerializer, CourseSerializer

User = get_user_model()

logger = logging.getLogger(__name__)


class CoursesAppBaseAPIView(APIView):
    """Base API view for the courses app."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """Include request context for serializers."""
        return {"request": self.request}


# --- Course CRUD Operations ---


class CourseCreateView(CoursesAppBaseAPIView):
    """Create a course for the authenticated user."""

    permission_classes = [CanCreateCourse]

    @extend_schema(
        summary="Create a course",
        description=(
            "Create a new course. The creator is automatically added "
            "as a teacher membership."
        ),
        tags=["Courses"],
        request=CourseSerializer,
        responses={
            201: OpenApiResponse(
                description="Course successfully created.",
                response=CourseSerializer,
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
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Permission denied."),
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
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        logger.debug("Course creation requested by user %s", request.user)

        serializer = CourseSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        course = serializer.save()

        logger.info(
            "Course %s (%s) created by %s", course.title, course.pk, request.user
        )
        CourseMembership.objects.create(
            course=course,
            user=request.user,
            role="teacher",
            status="enrolled",
        )
        logger.debug(
            "Teacher membership created for user %s in course %s",
            request.user,
            course.pk,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --- Course Module Operations ---


class CourseModuleListCreateView(CoursesAppBaseAPIView):
    """List and create modules for a course."""

    permission_classes = [IsCourseMember]

    def get_queryset(self, course_id):
        return (
            CourseModule.objects.filter(course_id=course_id)
            .select_related("course", "content_type")
            .order_by("order")
        )

    @extend_schema(
        summary="List course modules",
        description=(
            "List all modules for a course, ordered by the order field. "
            "Only enrolled course members can view modules."
        ),
        tags=["Course Modules"],
        responses={
            200: OpenApiResponse(
                description="List of course modules.",
                response=CourseModuleSerializer(many=True),
            ),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Not a course member."),
            404: OpenApiResponse(description="Course not found."),
        },
    )
    def get(self, request, pk, *args, **kwargs):
        get_object_or_404(Course, pk=pk)
        modules = self.get_queryset(pk)
        serializer = CourseModuleSerializer(
            modules, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Create a course module",
        description=(
            "Create a new module in the course. Only course teachers can create modules. "
            "The course is automatically set from the URL."
        ),
        tags=["Course Modules"],
        request=inline_serializer(
            name="CourseModuleCreateRequest",
            fields={
                "title": serializers.CharField(
                    required=False, help_text="Module title"
                ),
                "order": serializers.IntegerField(
                    required=False, help_text="Display order (default 0)"
                ),
                "content_type": serializers.CharField(
                    help_text="Content type as 'app_label.model'"
                ),
                "object_id": serializers.IntegerField(
                    help_text="ID of the content object"
                ),
            },
        ),
        responses={
            201: OpenApiResponse(
                description="Module created successfully.",
                response=CourseModuleSerializer,
            ),
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can create modules."),
            404: OpenApiResponse(description="Course not found."),
        },
        examples=[
            OpenApiExample(
                "Create module",
                summary="Create a module linked to a chatroom",
                request_only=True,
                value={
                    "title": "Week 1: Introduction",
                    "order": 1,
                    "content_type": "chat.chatroom",
                    "object_id": 1,
                },
            ),
        ],
    )
    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        course = get_object_or_404(Course, pk=pk)

        data = request.data.copy()
        data["course"] = course.pk

        serializer = CourseModuleSerializer(
            data=data, context=self.get_serializer_context()
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info(
            "Module created in course %s (%s) by %s",
            course.title,
            course.pk,
            request.user,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseModuleDetailView(CoursesAppBaseAPIView):
    """Retrieve, update, or delete a single course module."""

    permission_classes = [IsCourseMember]

    def get_object(self, pk, module_id):
        return get_object_or_404(
            CourseModule.objects.select_related("course", "content_type"),
            pk=module_id,
            course_id=pk,
        )

    @extend_schema(
        summary="Retrieve a course module",
        description="Get details of a single module. Only enrolled course members can view.",
        tags=["Course Modules"],
        responses={
            200: OpenApiResponse(
                description="Module details.", response=CourseModuleSerializer
            ),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Not a course member."),
            404: OpenApiResponse(description="Module or course not found."),
        },
    )
    def get(self, request, pk, module_id, *args, **kwargs):
        module = self.get_object(pk, module_id)
        serializer = CourseModuleSerializer(
            module, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Update a course module",
        description=(
            "Partially update a module's fields (title, order, content_type, object_id). "
            "Only course teachers can update modules."
        ),
        tags=["Course Modules"],
        request=CourseModuleSerializer,
        responses={
            200: OpenApiResponse(
                description="Module updated successfully.",
                response=CourseModuleSerializer,
            ),
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can update modules."),
            404: OpenApiResponse(description="Module or course not found."),
        },
    )
    @transaction.atomic
    def patch(self, request, pk, module_id, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        module = self.get_object(pk, module_id)
        serializer = CourseModuleSerializer(
            module,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info(
            "Module %s updated in course %s by %s",
            module_id,
            pk,
            request.user,
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Delete a course module",
        description="Remove a module from the course. Only course teachers can delete modules.",
        tags=["Course Modules"],
        responses={
            204: OpenApiResponse(description="Module deleted successfully."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can delete modules."),
            404: OpenApiResponse(description="Module or course not found."),
        },
    )
    @transaction.atomic
    def delete(self, request, pk, module_id, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        module = self.get_object(pk, module_id)
        logger.info(
            "Module %s deleted from course %s by %s",
            module_id,
            pk,
            request.user,
        )
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
