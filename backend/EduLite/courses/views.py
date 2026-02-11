import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import exceptions, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, CourseMembership, CourseModule
from .pagination import CoursePagination
from .permissions import CanCreateCourse, IsCourseMember, IsCourseTeacher
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    CourseMembershipSerializer,
    CourseModuleSerializer,
    CourseSerializer,
)

User = get_user_model()

logger = logging.getLogger(__name__)


class CoursesAppBaseAPIView(APIView):
    """Base API view for the courses app."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """Include request context for serializers."""
        return {"request": self.request}


# --- Course CRUD Operations ---


class CourseListCreateView(CoursesAppBaseAPIView):
    """List and create courses."""

    @extend_schema(
        summary="List courses",
        description=(
            "Returns a paginated list of courses visible to the requesting user. "
            "Public courses are visible to all authenticated users. "
            "Private and restricted courses are only visible to their members.\n\n"
            "Supports filtering by visibility, subject, language, country, "
            "and mine (returns only courses the user is a member of)."
        ),
        tags=["Courses"],
        parameters=[
            OpenApiParameter(
                name="visibility",
                type=OpenApiTypes.STR,
                description="Filter by visibility (public, restricted, private).",
            ),
            OpenApiParameter(
                name="subject",
                type=OpenApiTypes.STR,
                description="Filter by subject.",
            ),
            OpenApiParameter(
                name="language",
                type=OpenApiTypes.STR,
                description="Filter by language.",
            ),
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.STR,
                description="Filter by country.",
            ),
            OpenApiParameter(
                name="mine",
                type=OpenApiTypes.BOOL,
                description="If true, return only courses the user is a member of.",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Paginated list of courses.",
                response=CourseListSerializer(many=True),
            ),
            401: OpenApiResponse(description="Authentication required."),
        },
    )
    def get(self, request, *args, **kwargs):
        courses = (
            Course.objects.annotate(
                member_count=Count(
                    "memberships",
                    filter=Q(memberships__status="enrolled"),
                    distinct=True,
                )
            )
            .filter(
                Q(visibility="public")
                | Q(
                    memberships__user=request.user,
                    memberships__status="enrolled",
                )
            )
            .distinct()
            .order_by("-id")
        )

        # Apply query param filters
        visibility = request.query_params.get("visibility")
        if visibility:
            courses = courses.filter(visibility=visibility)

        subject = request.query_params.get("subject")
        if subject:
            courses = courses.filter(subject=subject)

        language = request.query_params.get("language")
        if language:
            courses = courses.filter(language=language)

        country = request.query_params.get("country")
        if country:
            courses = courses.filter(country=country)

        mine = request.query_params.get("mine")
        if mine and mine.lower() in ("true", "1"):
            courses = courses.filter(
                memberships__user=request.user,
                memberships__status="enrolled",
            )

        paginator = CoursePagination()
        page = paginator.paginate_queryset(courses, request, view=self)
        serializer = CourseListSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return paginator.get_paginated_response(serializer.data)

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
        if not CanCreateCourse().has_permission(request, self):
            raise exceptions.PermissionDenied(CanCreateCourse.message)

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


class CourseDetailView(CoursesAppBaseAPIView):
    """Retrieve, update, or delete a single course."""

    permission_classes = [IsCourseMember]

    def get_object(self, pk):
        return get_object_or_404(
            Course.objects.prefetch_related(
                "memberships__user", "course_modules__content_type"
            ),
            pk=pk,
        )

    @extend_schema(
        summary="Retrieve a course",
        description=(
            "Get full details of a course including members, modules, "
            "and the requesting user's role."
        ),
        tags=["Courses"],
        responses={
            200: OpenApiResponse(
                description="Course details.",
                response=CourseDetailSerializer,
            ),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Not a course member."),
            404: OpenApiResponse(description="Course not found."),
        },
    )
    def get(self, request, pk, *args, **kwargs):
        course = self.get_object(pk)
        serializer = CourseDetailSerializer(
            course, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Update a course",
        description=(
            "Partially update course fields. Only course teachers can update."
        ),
        tags=["Courses"],
        request=CourseSerializer,
        responses={
            200: OpenApiResponse(
                description="Course updated successfully.",
                response=CourseSerializer,
            ),
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can update courses."),
            404: OpenApiResponse(description="Course not found."),
        },
    )
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        course = self.get_object(pk)
        serializer = CourseSerializer(
            course,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info(
            "Course %s (%s) updated by %s",
            course.title,
            course.pk,
            request.user,
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Delete a course",
        description=(
            "Delete a course and all associated data (memberships, modules, etc.). "
            "Only course teachers can delete."
        ),
        tags=["Courses"],
        responses={
            204: OpenApiResponse(description="Course deleted successfully."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can delete courses."),
            404: OpenApiResponse(description="Course not found."),
        },
    )
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        course = self.get_object(pk)
        logger.info(
            "Course %s (%s) deleted by %s",
            course.title,
            course.pk,
            request.user,
        )
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


# --- Course Membership Operations ---


class CourseMembershipListInviteView(CoursesAppBaseAPIView):
    """List course members and invite new users."""

    permission_classes = [IsCourseMember]

    @extend_schema(
        summary="List course members",
        description=(
            "Returns a paginated list of memberships for the course. "
            "Only enrolled course members can view."
        ),
        tags=["Course Members"],
        responses={
            200: OpenApiResponse(
                description="Paginated list of course members.",
                response=CourseMembershipSerializer(many=True),
            ),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Not a course member."),
            404: OpenApiResponse(description="Course not found."),
        },
    )
    def get(self, request, pk, *args, **kwargs):
        get_object_or_404(Course, pk=pk)
        memberships = (
            CourseMembership.objects.filter(course_id=pk)
            .select_related("user", "course")
            .order_by("pk")
        )
        paginator = CoursePagination()
        page = paginator.paginate_queryset(memberships, request, view=self)
        serializer = CourseMembershipSerializer(
            page, many=True, context=self.get_serializer_context()
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Invite a user to the course",
        description=(
            "Invite a user by their ID. Only course teachers can invite. "
            "The membership is created with status 'invited'."
        ),
        tags=["Course Members"],
        request=inline_serializer(
            name="CourseMembershipInviteRequest",
            fields={
                "user": serializers.IntegerField(help_text="User ID to invite"),
                "role": serializers.ChoiceField(
                    choices=["student", "assistant", "teacher"],
                    required=False,
                    help_text="Role for the invited user (default: student)",
                ),
            },
        ),
        responses={
            201: OpenApiResponse(
                description="User invited successfully.",
                response=CourseMembershipSerializer,
            ),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can invite users."),
            404: OpenApiResponse(description="Course or user not found."),
            409: OpenApiResponse(
                description="User is already a member of this course."
            ),
        },
        examples=[
            OpenApiExample(
                "Invite student",
                summary="Invite a user as a student",
                request_only=True,
                value={"user": 5, "role": "student"},
            ),
        ],
    )
    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        course = get_object_or_404(Course, pk=pk)
        user_id = request.data.get("user")
        user = get_object_or_404(User, pk=user_id)

        if CourseMembership.objects.filter(course=course, user=user).exists():
            return Response(
                {"detail": "User is already a member of this course."},
                status=status.HTTP_409_CONFLICT,
            )

        role = request.data.get("role", "student")
        membership = CourseMembership.objects.create(
            course=course,
            user=user,
            role=role,
            status="invited",
        )
        logger.info(
            "User %s invited to course %s (%s) by %s",
            user.username,
            course.title,
            course.pk,
            request.user,
        )
        serializer = CourseMembershipSerializer(
            membership, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseMembershipDetailView(CoursesAppBaseAPIView):
    """Approve, deny, change role, or remove a course membership."""

    permission_classes = [IsCourseMember]

    def get_object(self, pk, membership_id):
        return get_object_or_404(
            CourseMembership.objects.select_related("user", "course"),
            pk=membership_id,
            course_id=pk,
        )

    def _is_last_teacher(self, membership):
        """Check if this membership is the only enrolled teacher in the course."""
        if membership.role != "teacher":
            return False
        return (
            not CourseMembership.objects.filter(
                course=membership.course, role="teacher", status="enrolled"
            )
            .exclude(pk=membership.pk)
            .exists()
        )

    @extend_schema(
        summary="Update a course membership",
        description=(
            "Partially update a membership's status or role. Teacher-only.\n\n"
            "- **Approve**: set status to 'enrolled' (from pending/invited)\n"
            "- **Deny**: set status to 'denied' (deletes the membership, returns 204)\n"
            "- **Change role**: update the role field\n\n"
            "Cannot demote the last teacher in a course (returns 409)."
        ),
        tags=["Course Members"],
        request=inline_serializer(
            name="CourseMembershipUpdateRequest",
            fields={
                "status": serializers.ChoiceField(
                    choices=["enrolled", "denied"],
                    required=False,
                    help_text="New status (use 'denied' to remove pending/invited member)",
                ),
                "role": serializers.ChoiceField(
                    choices=["student", "assistant", "teacher"],
                    required=False,
                    help_text="New role",
                ),
            },
        ),
        responses={
            200: OpenApiResponse(
                description="Membership updated.",
                response=CourseMembershipSerializer,
            ),
            204: OpenApiResponse(description="Membership denied and deleted."),
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can manage members."),
            404: OpenApiResponse(description="Membership not found."),
            409: OpenApiResponse(description="Cannot demote the last teacher."),
        },
    )
    @transaction.atomic
    def patch(self, request, pk, membership_id, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        membership = self.get_object(pk, membership_id)

        # Deny = delete the membership
        if request.data.get("status") == "denied":
            logger.info(
                "Membership %s denied in course %s by %s",
                membership_id,
                pk,
                request.user,
            )
            membership.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Last-teacher protection on role change
        new_role = request.data.get("role")
        if (
            new_role
            and new_role != "teacher"
            and membership.role == "teacher"
            and self._is_last_teacher(membership)
        ):
            return Response(
                {"detail": "Cannot demote the last teacher in the course."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = CourseMembershipSerializer(
            membership,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info(
            "Membership %s updated in course %s by %s",
            membership_id,
            pk,
            request.user,
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Remove a course member",
        description=(
            "Remove a member from the course. Teacher-only. "
            "Cannot remove the last teacher (returns 409)."
        ),
        tags=["Course Members"],
        responses={
            204: OpenApiResponse(description="Member removed."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only teachers can remove members."),
            404: OpenApiResponse(description="Membership not found."),
            409: OpenApiResponse(description="Cannot remove the last teacher."),
        },
    )
    @transaction.atomic
    def delete(self, request, pk, membership_id, *args, **kwargs):
        if not IsCourseTeacher().has_permission(request, self):
            raise exceptions.PermissionDenied(IsCourseTeacher.message)

        membership = self.get_object(pk, membership_id)

        if self._is_last_teacher(membership):
            return Response(
                {"detail": "Cannot remove the last teacher in the course."},
                status=status.HTTP_409_CONFLICT,
            )

        logger.info(
            "Member %s removed from course %s by %s",
            membership.user.username,
            pk,
            request.user,
        )
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Course Enrollment ---


class CourseEnrollView(CoursesAppBaseAPIView):
    """Join or leave a course."""

    @extend_schema(
        summary="Join a course",
        description=(
            "Join a course as a student.\n\n"
            "- **Public** courses: immediately enrolled.\n"
            "- **Restricted** courses with join requests enabled: membership created as pending.\n"
            "- **Restricted** without join requests or **private** courses: denied (403).\n\n"
            "Returns 409 if already a member."
        ),
        tags=["Course Enrollment"],
        responses={
            201: OpenApiResponse(
                description="Successfully joined or request submitted.",
                response=CourseMembershipSerializer,
            ),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Course does not allow joining."),
            404: OpenApiResponse(description="Course not found."),
            409: OpenApiResponse(description="Already a member of this course."),
        },
    )
    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        course = get_object_or_404(Course, pk=pk)

        if CourseMembership.objects.filter(course=course, user=request.user).exists():
            return Response(
                {"detail": "You are already a member of this course."},
                status=status.HTTP_409_CONFLICT,
            )

        if course.visibility == "public":
            membership_status = "enrolled"
        elif course.visibility == "restricted" and course.allow_join_requests:
            membership_status = "pending"
        else:
            return Response(
                {"detail": "This course does not allow joining."},
                status=status.HTTP_403_FORBIDDEN,
            )

        membership = CourseMembership.objects.create(
            course=course,
            user=request.user,
            role="student",
            status=membership_status,
        )
        logger.info(
            "User %s joined course %s (%s) with status %s",
            request.user.username,
            course.title,
            course.pk,
            membership_status,
        )
        serializer = CourseMembershipSerializer(
            membership, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Leave a course",
        description=(
            "Remove yourself from a course. "
            "The last teacher in a course cannot leave (returns 409)."
        ),
        tags=["Course Enrollment"],
        responses={
            204: OpenApiResponse(description="Successfully left the course."),
            401: OpenApiResponse(description="Authentication required."),
            404: OpenApiResponse(description="Not a member of this course."),
            409: OpenApiResponse(description="Cannot leave as the last teacher."),
        },
    )
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        membership = (
            CourseMembership.objects.filter(course_id=pk, user=request.user)
            .select_related("course")
            .first()
        )

        if not membership:
            return Response(
                {"detail": "You are not a member of this course."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            membership.role == "teacher"
            and not CourseMembership.objects.filter(
                course_id=pk, role="teacher", status="enrolled"
            )
            .exclude(pk=membership.pk)
            .exists()
        ):
            return Response(
                {"detail": "Cannot leave as the last teacher in the course."},
                status=status.HTTP_409_CONFLICT,
            )

        logger.info(
            "User %s left course %s",
            request.user.username,
            pk,
        )
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
