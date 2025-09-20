# users/views.py
import logging
import json
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from .models import UserProfile, ProfileFriendRequest, UserProfilePrivacySettings

from .serializers import (
    UserSerializer,
    UserSearchSerializer,
    GroupSerializer,
    UserRegistrationSerializer,
    ProfileSerializer,
    ProfileFriendRequestSerializer,
    UserProfilePrivacySettingsSerializer,
)

from .permissions import (
    IsProfileOwnerOrAdmin,
    IsUserOwnerOrAdmin,
    IsAdminUserOrReadOnly,
    IsFriendRequestReceiver,
    IsFriendRequestReceiverOrSender,
)
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
import json
import base64

logger = logging.getLogger(__name__)
performance_logger = logging.getLogger("performance")


class UsersAppBaseAPIView(APIView):
    """
    Enhanced base API view with automatic performance monitoring and alerting.
    Monitors response time and payload size, triggering alerts when thresholds exceeded.

    **Monitoring Thresholds:**
    - Response Time: 100ms (configurable via PERFORMANCE_MONITORING['RESPONSE_TIME_THRESHOLD'])
    - Payload Size: 10KB (configurable via PERFORMANCE_MONITORING['PAYLOAD_SIZE_THRESHOLD_KB'])

    **Configuration in settings.py:**
    PERFORMANCE_MONITORING = {
        'ENABLED': True,  # Enable monitoring
        'RESPONSE_TIME_THRESHOLD': 100,  # milliseconds
        'PAYLOAD_SIZE_THRESHOLD_KB': 10,  # kilobytes
        'LOG_ALL_REQUESTS': False,  # Only log threshold violations
        'LOG_LEVEL': 'WARNING',  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        This is useful for HATEOAS link generation or other context-aware serialization.
        """
        return {"request": self.request}


@extend_schema()
class UserListView(UsersAppBaseAPIView):
    """
    OPTIMIZED API view to list all users (with pagination).
    - GET: Returns a paginated list of users.
    Supports dynamic page_size via query parameter for performance testing.
    """

    # CLASS-LEVEL CONFIGURATION
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Get the queryset with proper select_related to avoid N+1 queries.
        """
        return (
            User.objects.select_related(
                "profile",  # For profile_url field and privacy checks
                "profile__privacy_settings",  # For privacy settings in serializer methods
            )
            .prefetch_related(
                "groups",  # If you're including group information
            )
            .order_by("-date_joined")
        )

    @extend_schema(
        summary="List all users",
        description="Returns a paginated list of all users in the system. Supports dynamic page_size for performance testing.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number (default: 1)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page (default: 10, max: 100)",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved list of users",
                response=inline_serializer(
                    name="UserListPaginatedResponse",
                    fields={
                        "count": serializers.IntegerField(
                            help_text="Total number of users"
                        ),
                        "next": serializers.URLField(
                            allow_null=True, help_text="URL to next page"
                        ),
                        "previous": serializers.URLField(
                            allow_null=True, help_text="URL to previous page"
                        ),
                        "results": UserSerializer(many=True),
                    },
                ),
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided",
                response=inline_serializer(
                    name="UnauthorizedError", fields={"detail": serializers.CharField()}
                ),
            ),
        },
        tags=["Users"],
    )
    def get(self, request, *args, **kwargs):
        """Handles LIST with minimal database queries."""
        # Get optimized queryset
        users = self.get_queryset()

        # Create paginator instance (not class-level)
        paginator = self.pagination_class()
        paginator.page_size = 10  # Default page size
        paginator.max_page_size = 100

        # Allow dynamic page_size for performance testing
        page_size = request.query_params.get("page_size")
        if page_size:
            try:
                page_size = int(page_size)
                # Respect max_page_size limit
                if page_size <= paginator.max_page_size:
                    paginator.page_size = page_size
            except (ValueError, TypeError):
                pass  # Invalid page_size, use default

        # Paginate the queryset
        page = paginator.paginate_queryset(users, request, view=self)

        if page is not None:
            # Use class, not instance
            serializer = self.serializer_class(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)

        # When pagination is not active, return full list
        serializer = self.serializer_class(
            users, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


@extend_schema()
class UserRegistrationView(UsersAppBaseAPIView):
    """
    API view to register a new user.
    - POST: Creates a new user.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account. If email verification is enabled, sends a verification email.\n\n**Password Requirements:**\n- Minimum 8 characters\n- Cannot be entirely numeric\n- Cannot be too similar to username or email\n- Cannot be a commonly used password",
        request=UserRegistrationSerializer,
        examples=[
            OpenApiExample(
                "Complete Registration",
                value={
                    "username": "johndoe123",
                    "email": "john.doe@gmail.com",
                    "password": "SecurePass123!",
                    "password2": "SecurePass123!",
                    "first_name": "John",
                    "last_name": "Doe",
                },
                request_only=True,
                description="Full registration with all optional fields",
            ),
            OpenApiExample(
                "Minimal Registration",
                value={
                    "username": "janedoe456",
                    "email": "jane.doe@gmail.com",
                    "password": "MyPassword2024",
                    "password2": "MyPassword2024",
                },
                request_only=True,
                description="Minimal registration with only required fields",
            ),
        ],
        responses={
            201: OpenApiResponse(
                description="User created successfully",
                response=inline_serializer(
                    name="UserRegistrationResponse",
                    fields={
                        "message": serializers.CharField(help_text="Success message"),
                        "user_id": serializers.IntegerField(
                            help_text="ID of created user", required=False
                        ),
                        "username": serializers.CharField(
                            help_text="Username of created user", required=False
                        ),
                        "email": serializers.EmailField(
                            help_text="Email of created user", required=False
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "With Verification",
                        value={
                            "message": "Verification email sent. Please check your email to complete registration."
                        },
                        description="Response when email verification is required",
                    ),
                    OpenApiExample(
                        "Without Verification",
                        value={
                            "message": "User created successfully. Verification email sent.",
                            "user_id": 123,
                            "username": "johndoe",
                            "email": "john@example.com",
                        },
                        description="Response when user is created immediately",
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Invalid registration data",
                response=inline_serializer(
                    name="RegistrationValidationError",
                    fields={
                        "username": serializers.ListField(
                            child=serializers.CharField(), required=False
                        ),
                        "email": serializers.ListField(
                            child=serializers.CharField(), required=False
                        ),
                        "password": serializers.ListField(
                            child=serializers.CharField(), required=False
                        ),
                        "password2": serializers.ListField(
                            child=serializers.CharField(), required=False
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Username Taken",
                        value={
                            "username": ["A user with that username already exists."]
                        },
                    ),
                    OpenApiExample(
                        "Password Mismatch",
                        value={"password2": ["Passwords do not match."]},
                    ),
                    OpenApiExample(
                        "Invalid Email",
                        value={"email": ["Enter a valid email address."]},
                    ),
                    OpenApiExample(
                        "Password Too Short",
                        value={
                            "password": [
                                "This password is too short. It must contain at least 8 characters."
                            ]
                        },
                    ),
                    OpenApiExample(
                        "Password Too Common",
                        value={"password": ["This password is too common."]},
                    ),
                    OpenApiExample(
                        "Password Entirely Numeric",
                        value={"password": ["This password is entirely numeric."]},
                    ),
                ],
            ),
        },
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):  # Handles CREATE
        serializer = UserRegistrationSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            result = serializer.save()  # Returns either User or dict

            # Check if email verification is required
            from django.conf import settings

            require_verification = getattr(
                settings, "USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP", False
            )

            if require_verification:
                # Email verification required - return message only
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                # User created immediately - format response with user_id
                response_data = {
                    "message": "User created successfully. Verification email sent.",
                    "user_id": result.id,
                    "username": result.username,
                    "email": result.email,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema()
class UserRetrieveView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user by their PK.
    - GET: Retrieves a user.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset_all = User.objects.select_related(
        "profile", "profile__privacy_settings"
    ).prefetch_related(
        "groups"
    )  # Optimized queryset for object lookup
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        return get_object_or_404(self.queryset_all, pk=pk)

    @extend_schema(
        summary="Retrieve user details",
        description="Get detailed information about a specific user by their ID.",
        responses={
            200: OpenApiResponse(
                description="User details retrieved successfully",
                response=UserSerializer,
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided",
                response=inline_serializer(
                    name="UnauthorizedError", fields={"detail": serializers.CharField()}
                ),
            ),
            404: OpenApiResponse(
                description="User not found",
                response=inline_serializer(
                    name="NotFoundError", fields={"detail": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample("User Not Found", value={"detail": "Not found."})
                ],
            ),
        },
        tags=["Users"],
    )
    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, context=self.get_serializer_context()
        )
        return Response(serializer.data)


@extend_schema()
class UserUpdateDeleteView(UsersAppBaseAPIView):
    """
    API view to update or delete a specific user by their PK.
    Inherits from UsersAppBaseAPIView.
    - PUT: Updates a user.
    - PATCH: Partially updates a user.
    - DELETE: Deletes a user.
    """

    permission_classes = [IsUserOwnerOrAdmin]
    queryset_all = User.objects.select_related("profile", "profile__privacy_settings")
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        summary="Update user",
        description="Fully update a user's information. Only the user themselves or an admin can perform this action.",
        request=UserSerializer,
        examples=[
            OpenApiExample(
                "Update User",
                value={
                    "username": "johndoe",
                    "email": "john@example.com",
                    "groups": [],
                    "first_name": "John",
                    "last_name": "Doe",
                },
                request_only=True,
                description="Example user update with empty groups",
            )
        ],
        responses={
            200: OpenApiResponse(
                description="User updated successfully", response=UserSerializer
            ),
            400: OpenApiResponse(
                description="Invalid data provided",
                response=inline_serializer(
                    name="ValidationError",
                    fields={"field_name": serializers.CharField()},
                ),
            ),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(
                description="Permission denied",
                response=inline_serializer(
                    name="ForbiddenError", fields={"detail": serializers.CharField()}
                ),
            ),
            404: OpenApiResponse(description="User not found"),
        },
        tags=["Users"],
    )
    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update user",
        description="Partially update a user's information. Only the user themselves or an admin can perform this action.",
        request=UserSerializer,
        examples=[
            OpenApiExample(
                "Partial Update",
                value={"first_name": "Jane", "groups": []},
                request_only=True,
                description="Example partial update with only some fields",
            )
        ],
        responses={
            200: OpenApiResponse(
                description="User partially updated successfully",
                response=UserSerializer,
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="User not found"),
        },
        tags=["Users"],
    )
    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, data=request.data, partial=True, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete user",
        description="Delete a user account. Only the user themselves or an admin can perform this action.",
        responses={
            202: OpenApiResponse(
                description="User deleted successfully",
                response=inline_serializer(
                    name="DeleteSuccessResponse",
                    fields={"message": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Success", value={"message": "User deleted successfully."}
                    )
                ],
            ),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="User not found"),
            500: OpenApiResponse(
                description="Server error",
                response=inline_serializer(
                    name="ServerError", fields={"message": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample(
                        "Delete Failed", value={"message": "User could not be deleted!"}
                    )
                ],
            ),
        },
        tags=["Users"],
    )
    def delete(self, request, pk, *args, **kwargs):  # Handles DESTROY
        user = self.get_object(pk)
        # Consider any pre-delete logic or checks here
        try:
            user.delete()
            return Response(
                {"message": "User deleted successfully."},
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as e:
            logger.error(f"Failed to delete user {pk}: {str(e)}")
            return Response(
                {"message": "User could not be deleted!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# --- Group API Views ---


@extend_schema()
class GroupListCreateView(UsersAppBaseAPIView):
    """
    API view to list all groups (with pagination) or create a new group.
    - GET: Returns a paginated list of groups.
    - POST: Creates a new group.
    """

    permission_classes = [IsAdminUserOrReadOnly]
    queryset_all = Group.objects.all().order_by("name")
    serializer_class_instance = GroupSerializer
    pagination_class_instance = PageNumberPagination
    pagination_class_instance.page_size = 10

    @extend_schema(
        summary="List all groups",
        description="Returns a paginated list of all groups in the system.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved list of groups",
                response=inline_serializer(
                    name="GroupListPaginatedResponse",
                    fields={
                        "count": serializers.IntegerField(),
                        "next": serializers.URLField(allow_null=True),
                        "previous": serializers.URLField(allow_null=True),
                        "results": GroupSerializer(many=True),
                    },
                ),
            ),
            401: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Groups"],
    )
    def get(self, request, *args, **kwargs):  # Handles LIST
        groups = self.queryset_all
        paginator = self.pagination_class_instance()
        page = paginator.paginate_queryset(groups, request, view=self)
        if page is not None:
            serializer = self.serializer_class_instance(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)
        # When pagination is not active or applicable, just return the full list
        serializer = self.serializer_class_instance(
            groups, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new group",
        description="Creates a new group. Admin privileges required.",
        request=GroupSerializer,
        responses={
            201: OpenApiResponse(
                description="Group created successfully", response=GroupSerializer
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied - admin only"),
        },
        tags=["Groups"],
    )
    def post(self, request, *args, **kwargs):  # Handles CREATE
        serializer = self.serializer_class_instance(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema()
class GroupRetrieveUpdateDestroyView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific group by its PK.
    Inherits from UsersAppBaseAPIView.
    - GET: Retrieves a group.
    - PUT: Updates a group.
    - PATCH: Partially updates a group.
    - DELETE: Deletes a group.
    """

    permission_classes = [IsAdminUserOrReadOnly]
    queryset_all = Group.objects.all()
    serializer_class_instance = GroupSerializer

    def get_object(self, pk):
        return get_object_or_404(self.queryset_all, pk=pk)

    @extend_schema(
        summary="Retrieve group details",
        description="Get detailed information about a specific group.",
        responses={
            200: OpenApiResponse(
                description="Group details retrieved successfully",
                response=GroupSerializer,
            ),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Group not found"),
        },
        tags=["Groups"],
    )
    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Update group",
        description="Fully update a group's information. Admin privileges required.",
        request=GroupSerializer,
        responses={
            200: OpenApiResponse(
                description="Group updated successfully", response=GroupSerializer
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied - admin only"),
            404: OpenApiResponse(description="Group not found"),
        },
        tags=["Groups"],
    )
    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update group",
        description="Partially update a group's information. Admin privileges required.",
        request=GroupSerializer,
        responses={
            200: OpenApiResponse(
                description="Group partially updated successfully",
                response=GroupSerializer,
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied - admin only"),
            404: OpenApiResponse(description="Group not found"),
        },
        tags=["Groups"],
    )
    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete group",
        description="Delete a group. Admin privileges required.",
        responses={
            204: OpenApiResponse(description="Group deleted successfully"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied - admin only"),
            404: OpenApiResponse(description="Group not found"),
        },
        tags=["Groups"],
    )
    def delete(self, request, pk, *args, **kwargs):  # Handles DESTROY
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -- User Profile API Views -- ##


@extend_schema()
class UserProfileRetrieveUpdateView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user profile by their PK.
    Inherits from UsersAppBaseAPIView.
    - GET: Retrieves a user profile.
    - PUT: Updates a user profile.
    - PATCH: Partially updates a user profile.
    """

    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerOrAdmin]
    queryset_all = UserProfile.objects.all()  # Base queryset for object lookup
    serializer_class_instance = ProfileSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the UserProfile object by its pk.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(
            self.request, obj
        )  # DRF's way to check permissions on the object
        return obj

    @extend_schema(
        summary="Retrieve user profile",
        description="Get detailed profile information for a specific user. Privacy settings are respected.",
        responses={
            200: OpenApiResponse(
                description="Profile retrieved successfully", response=ProfileSerializer
            ),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Profile not found"),
        },
        tags=["User Profiles"],
    )
    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Update user profile",
        description="Fully update a user's profile. Only the profile owner or an admin can perform this action. Note: To upload a picture, use multipart/form-data instead of JSON.",
        request=ProfileSerializer,
        examples=[
            OpenApiExample(
                "Complete Profile Update",
                value={
                    "bio": "I am a software developer passionate about education technology",
                    "occupation": "developer",
                    "country": "US",
                    "preferred_language": "en",
                    "secondary_language": "es",
                    "website_url": "https://example.com",
                    "friends": [],
                },
                request_only=True,
                description="Full profile update with all fields (except picture)",
            ),
            OpenApiExample(
                "Minimal Profile Update",
                value={
                    "bio": None,
                    "occupation": None,
                    "country": None,
                    "preferred_language": None,
                    "secondary_language": None,
                    "website_url": None,
                    "friends": [],
                },
                request_only=True,
                description="Clear all optional fields",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully", response=ProfileSerializer
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Profile not found"),
        },
        tags=["User Profiles"],
    )
    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update user profile",
        description="Partially update a user's profile. Only the profile owner or an admin can perform this action. Only include fields you want to update.",
        request=ProfileSerializer,
        examples=[
            OpenApiExample(
                "Update Bio Only",
                value={"bio": "Updated bio - now working in AI research"},
                request_only=True,
                description="Update only the bio field",
            ),
            OpenApiExample(
                "Update Location and Language",
                value={"country": "CA", "preferred_language": "fr"},
                request_only=True,
                description="Update country and language preferences",
            ),
            OpenApiExample(
                "Add Friends",
                value={"friends": [2, 3, 5]},
                request_only=True,
                description="Update friends list with user IDs",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Profile partially updated successfully",
                response=ProfileSerializer,
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Profile not found"),
        },
        tags=["User Profiles"],
    )
    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema()
class UserSearchView(UsersAppBaseAPIView):
    """
    API view to search for users by username, first name, or last name.
    Accepts a query parameter 'q'.
    - GET: Returns a paginated list of matching active users with privacy controls.

    Note: Anonymous users can search but will only see users with 'everyone' visibility.
    """

    permission_classes = [permissions.AllowAny]  # Allow anonymous users to search
    serializer_class_instance = (
        UserSearchSerializer  # Use lightweight search serializer
    )
    pagination_class_instance = PageNumberPagination

    @extend_schema(
        summary="Search users",
        description="Search for users by username, first name, or last name. Privacy settings are respected - anonymous users only see public profiles.",
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
                description="Page number",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page (default: 10, max: 100)",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Search results",
                response=inline_serializer(
                    name="UserSearchPaginatedResponse",
                    fields={
                        "count": serializers.IntegerField(),
                        "next": serializers.URLField(allow_null=True),
                        "previous": serializers.URLField(allow_null=True),
                        "results": UserSearchSerializer(many=True),
                    },
                ),
            ),
            400: OpenApiResponse(
                description="Invalid search query",
                response=inline_serializer(
                    name="SearchError", fields={"detail": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample(
                        "Query Too Short",
                        value={
                            "detail": "Search query must be at least 2 characters long."
                        },
                    )
                ],
            ),
        },
        tags=["Users"],
    )
    def get(self, request, *args, **kwargs):
        from .logic.user_search_logic import execute_user_search

        search_query = request.query_params.get("q", "").strip()
        requesting_user = request.user if request.user.is_authenticated else None

        # Check if admin should bypass privacy filters
        bypass_privacy = requesting_user and requesting_user.is_superuser

        if not bypass_privacy:
            bypass_privacy = False

        # Get page_size from query params (default 10)
        page_size = request.query_params.get("page_size", "10")
        try:
            page_size = int(page_size)
            # Limit page size to prevent abuse
            page_size = min(max(page_size, 1), 100)
        except (ValueError, TypeError):
            page_size = 10

        # Execute the search with privacy controls using logic functions
        success, queryset, paginator, error_response = execute_user_search(
            search_query=search_query,
            requesting_user=requesting_user,
            request=request,
            view_instance=self,
            min_query_length=2,
            page_size=page_size,
            bypass_privacy_filters=bypass_privacy,
        )

        # Return error response if validation failed
        if not success:
            return error_response

        # Handle paginated response
        if paginator is not None:
            # Get the page data that was set during pagination
            page_data = paginator.page
            serializer = self.serializer_class_instance(
                page_data, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)

        # Handle non-paginated response
        serializer = self.serializer_class_instance(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


# -- Friend Request API Views -- ##


@extend_schema()
class AcceptFriendRequestView(UsersAppBaseAPIView):
    """
    API view to accept a friend request.
    - POST: Accepts a friend request.
    """

    permission_classes = [IsAuthenticated, IsFriendRequestReceiver]

    @extend_schema(
        summary="Accept friend request",
        description="Accept a pending friend request. Only the receiver of the request can accept it.",
        responses={
            200: OpenApiResponse(
                description="Friend request accepted successfully",
                response=inline_serializer(
                    name="AcceptResponse", fields={"detail": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample(
                        "Success", value={"detail": "Friend request accepted."}
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Failed to accept friend request",
                response=inline_serializer(
                    name="AcceptError", fields={"detail": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample(
                        "Already Processed",
                        value={
                            "detail": "Failed to accept friend request. It might have been already processed or an error occurred."
                        },
                    )
                ],
            ),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(
                description="Permission denied - only receiver can accept"
            ),
            404: OpenApiResponse(description="Friend request not found"),
        },
        tags=["Friend Requests"],
    )
    def post(self, request, request_pk, *args, **kwargs):
        # Optimize query with select_related to prevent N+1 queries
        friend_request = get_object_or_404(
            ProfileFriendRequest.objects.select_related(
                "sender__user", "receiver__user"
            ),
            pk=request_pk,
        )

        # Manually trigger object-level permission check for APIView
        self.check_object_permissions(request, friend_request)

        if friend_request.accept():
            return Response(
                {"detail": "Friend request accepted."}, status=status.HTTP_200_OK
            )

        else:
            # This case might be hit if the request was deleted just before accept,
            # or if accept() method itself had an internal issue and returned False.
            return Response(
                {
                    "detail": "Failed to accept friend request. It might have been already processed or an error occurred."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema()
class DeclineFriendRequestView(UsersAppBaseAPIView):
    """
    API view to decline or cancel a friend request.
    - POST: Declines/Cancels a specific friend request identified by request_pk.
    """

    permission_classes = [IsAuthenticated, IsFriendRequestReceiverOrSender]

    @extend_schema(
        summary="Decline or cancel friend request",
        description="Decline a received friend request or cancel a sent friend request.",
        responses={
            200: OpenApiResponse(
                description="Friend request declined/canceled successfully",
                response=inline_serializer(
                    name="DeclineResponse", fields={"detail": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample(
                        "Declined",
                        value={"detail": "Friend request declined successfully."},
                    ),
                    OpenApiExample(
                        "Canceled",
                        value={"detail": "Friend request canceled successfully."},
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Failed to process friend request",
                response=inline_serializer(
                    name="DeclineError", fields={"detail": serializers.CharField()}
                ),
            ),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Friend request not found"),
        },
        tags=["Friend Requests"],
    )
    def post(self, request, request_pk, *args, **kwargs):
        friend_request = get_object_or_404(ProfileFriendRequest, pk=request_pk)

        self.check_object_permissions(request, friend_request)

        # Determine if the user was the sender (canceling) or receiver (declining)
        # for a more specific response message.
        action_taken_by_sender = friend_request.sender == request.user.profile

        if (
            friend_request.decline()
        ):  # Calls the model's decline method which deletes it
            if action_taken_by_sender:
                message = "Friend request canceled successfully."
            else:
                message = "Friend request declined successfully."
            return Response({"detail": message}, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "detail": "Failed to process the friend request. It might have been already actioned or an unexpected error occurred."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema()
class PendingFriendRequestListView(UsersAppBaseAPIView):
    """
    API view to list pending friend requests for the authenticated user.
    - GET: Returns a paginated list of received or sent friend requests.
    """

    serializer_class = ProfileFriendRequestSerializer  # Specify the serializer
    pagination_class = (
        PageNumberPagination  # Or your custom one, e.g., ChatRoomPagination if suitable
    )

    def get_queryset(self, request):
        user_profile = request.user.profile  # Assumes user.profile exists
        request_type = request.query_params.get("type", "received").lower()

        if request_type == "sent":
            # Get requests sent by the user
            queryset = user_profile.sent_friend_requests.all()
        elif request_type == "received":
            # Get requests received by the user
            queryset = user_profile.received_friend_requests.all()
        elif request_type == "all":
            # Get all pending requests (both sent and received)
            sent = user_profile.sent_friend_requests.all()
            received = user_profile.received_friend_requests.all()
            queryset = ProfileFriendRequest.objects.filter(
                Q(id__in=sent.values_list("id", flat=True))
                | Q(id__in=received.values_list("id", flat=True))
            )
        else:
            # Default to received for backwards compatibility
            queryset = user_profile.received_friend_requests.all()

        # Pre-fetch related user details for sender/receiver to optimize
        # Also select_related on sender and receiver to avoid N+1 for profile IDs
        # Include privacy_settings to avoid N+1 queries for privacy checks
        queryset = queryset.select_related(
            "sender",
            "receiver",
            "sender__user",
            "receiver__user",
            "sender__privacy_settings",
            "receiver__privacy_settings",
        )
        return queryset.order_by("-created_at")  # Ensure consistent ordering

    @extend_schema(
        summary="List pending friend requests",
        description="Get a paginated list of pending friend requests for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Type of requests to retrieve: "sent", "received", or "all" (default: "received")',
                enum=["sent", "received", "all"],
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="List of pending friend requests",
                response=inline_serializer(
                    name="FriendRequestListPaginatedResponse",
                    fields={
                        "count": serializers.IntegerField(),
                        "next": serializers.URLField(allow_null=True),
                        "previous": serializers.URLField(allow_null=True),
                        "results": ProfileFriendRequestSerializer(many=True),
                    },
                ),
            ),
            400: OpenApiResponse(
                description="User profile not found",
                response=inline_serializer(
                    name="ProfileError", fields={"detail": serializers.CharField()}
                ),
            ),
            401: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Friend Requests"],
    )
    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, "profile"):
            return Response(
                {"detail": "User profile not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset(request)

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is not None:
            # Pass context to serializer for HyperlinkedRelatedFields or SerializerMethodFields
            serializer = self.serializer_class(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)

        # Fallback if pagination is not applicable (e.g., queryset is empty and paginator returns None)
        serializer = self.serializer_class(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


@extend_schema()
class SendFriendRequestView(UsersAppBaseAPIView):
    """
    API view to send a new friend request.
    - POST: Creates a new ProfileFriendRequest.
    """

    # permission_classes is inherited from UsersAppBaseAPIView ([IsAuthenticated])

    @extend_schema(
        summary="Send friend request",
        description="Send a friend request to another user.",
        request=inline_serializer(
            name="SendFriendRequestInput",
            fields={
                "receiver_profile_id": serializers.IntegerField(
                    help_text="ID of the user profile to send request to"
                ),
                "message": serializers.CharField(
                    max_length=500,
                    required=False,
                    help_text="Optional message with the request",
                ),
            },
        ),
        responses={
            201: OpenApiResponse(
                description="Friend request sent successfully",
                response=inline_serializer(
                    name="SendFriendRequestResponse",
                    fields={
                        "detail": serializers.CharField(),
                        "request_id": serializers.IntegerField(),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "detail": "Friend request sent successfully.",
                            "request_id": 123,
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid request",
                response=inline_serializer(
                    name="SendRequestError", fields={"detail": serializers.CharField()}
                ),
                examples=[
                    OpenApiExample(
                        "Self Request",
                        value={
                            "detail": "You cannot send a friend request to yourself."
                        },
                    ),
                    OpenApiExample(
                        "Already Friends",
                        value={"detail": "You are already friends with this user."},
                    ),
                    OpenApiExample(
                        "Duplicate Request",
                        value={
                            "detail": "You have already sent a friend request to this user."
                        },
                    ),
                    OpenApiExample(
                        "Pending From Receiver",
                        value={
                            "detail": "This user has already sent you a friend request. Check your pending requests."
                        },
                    ),
                    OpenApiExample(
                        "Message Too Long",
                        value={"detail": "Message must be 500 characters or fewer."},
                    ),
                ],
            ),
            401: OpenApiResponse(description="Unauthorized"),
            404: OpenApiResponse(description="Receiver profile not found"),
        },
        tags=["Friend Requests"],
    )
    def post(self, request, *args, **kwargs):
        try:
            sender_profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Sender profile not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate input: receiver_profile_id
        receiver_profile_id = request.data.get("receiver_profile_id")
        if not receiver_profile_id:
            return Response(
                {"detail": "receiver_profile_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(receiver_profile_id, int):
            return Response(
                {"detail": "Invalid receiver_profile_id. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        receiver_profile = get_object_or_404(UserProfile, pk=receiver_profile_id)

        # 1. Self-request check
        if sender_profile == receiver_profile:
            return Response(
                {"detail": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Already friends check (using the UserProfile.friends M2M to User)
        if sender_profile.friends.filter(pk=receiver_profile.user.pk).exists():
            return Response(
                {"detail": "You are already friends with this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Check for existing pending request (in either direction)
        # This also covers the UniqueConstraint on the model but gives a nicer API error.
        existing_request = ProfileFriendRequest.objects.filter(
            (Q(sender=sender_profile) & Q(receiver=receiver_profile))
            | (Q(sender=receiver_profile) & Q(receiver=sender_profile))
        ).first()

        if existing_request:
            if existing_request.sender == sender_profile:
                message = "You have already sent a friend request to this user."
            else:
                message = "This user has already sent you a friend request. Check your pending requests."
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Get optional message
        message = request.data.get("message", "").strip()
        if len(message) > 500:
            return Response(
                {"detail": "Message must be 500 characters or fewer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If all checks pass, create the friend request
        try:
            friend_request = ProfileFriendRequest.objects.create(
                sender=sender_profile,
                receiver=receiver_profile,
                message=message if message else None,
            )
            return Response(
                {
                    "detail": "Friend request sent successfully.",
                    "request_id": friend_request.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            # Handle different ValidationError formats
            if hasattr(e, "message_dict"):
                return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
            elif hasattr(e, "messages"):
                return Response(
                    {"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:  # Catch IntegrityError from UniqueConstraint
            return Response(
                {
                    "detail": "A friend request between these users already exists or another integrity issue occurred."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# -- Privacy Settings API Views -- ##


@extend_schema()
class UserProfilePrivacySettingsRetrieveUpdateView(UsersAppBaseAPIView):
    """
    API view to retrieve and update user privacy settings.
    - GET: Returns the current user's privacy settings.
    - PUT/PATCH: Updates the current user's privacy settings.
    """

    serializer_class_instance = UserProfilePrivacySettingsSerializer

    def get_object(self):
        """
        Get the privacy settings for the current user.
        Creates privacy settings if they don't exist (defensive programming).
        """
        user_profile = get_object_or_404(UserProfile, user=self.request.user)

        # Ensure privacy settings exist (defensive programming)
        privacy_settings, created = UserProfilePrivacySettings.objects.get_or_create(
            user_profile=user_profile
        )

        if created:
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                "Created missing privacy settings for user %s",
                self.request.user.username,
            )

        return privacy_settings

    @extend_schema(
        summary="Get privacy settings",
        description="Retrieve the current user's privacy settings.",
        responses={
            200: OpenApiResponse(
                description="Privacy settings retrieved successfully",
                response=UserProfilePrivacySettingsSerializer,
            ),
            401: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Privacy Settings"],
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve the current user's privacy settings.
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Update privacy settings",
        description="Fully update the current user's privacy settings.",
        request=UserProfilePrivacySettingsSerializer,
        responses={
            200: OpenApiResponse(
                description="Privacy settings updated successfully",
                response=UserProfilePrivacySettingsSerializer,
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Privacy Settings"],
    )
    def put(self, request, *args, **kwargs):
        """
        Update the current user's privacy settings (full update).
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings,
            data=request.data,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update privacy settings",
        description="Partially update the current user's privacy settings.",
        request=UserProfilePrivacySettingsSerializer,
        responses={
            200: OpenApiResponse(
                description="Privacy settings partially updated successfully",
                response=UserProfilePrivacySettingsSerializer,
            ),
            400: OpenApiResponse(description="Invalid data provided"),
            401: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Privacy Settings"],
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update the current user's privacy settings.
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema()
class UserProfilePrivacySettingsChoicesView(UsersAppBaseAPIView):
    """
    API view to get available privacy setting choices.
    - GET: Returns the available choices for privacy settings fields.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get privacy setting choices",
        description="Retrieve available options for privacy settings fields.",
        responses={
            200: OpenApiResponse(
                description="Privacy setting choices",
                response=inline_serializer(
                    name="PrivacySettingsChoices",
                    fields={
                        "search_visibility": serializers.ListField(
                            child=inline_serializer(
                                name="Choice",
                                fields={
                                    "value": serializers.CharField(),
                                    "display_name": serializers.CharField(),
                                },
                            )
                        ),
                        "profile_visibility": serializers.ListField(
                            child=inline_serializer(
                                name="ProfileChoice",
                                fields={
                                    "value": serializers.CharField(),
                                    "display_name": serializers.CharField(),
                                },
                            )
                        ),
                    },
                ),
                examples=[
                    OpenApiExample(
                        "Choices",
                        value={
                            "search_visibility": [
                                {"value": "everyone", "display_name": "Everyone"},
                                {"value": "friends", "display_name": "Friends Only"},
                                {"value": "nobody", "display_name": "Nobody"},
                            ],
                            "profile_visibility": [
                                {"value": "everyone", "display_name": "Everyone"},
                                {"value": "friends", "display_name": "Friends Only"},
                                {"value": "nobody", "display_name": "Nobody"},
                            ],
                        },
                    )
                ],
            ),
            401: OpenApiResponse(description="Unauthorized"),
        },
        tags=["Privacy Settings"],
    )
    def get(self, request, *args, **kwargs):
        """
        Return available choices for privacy settings.
        """
        from .models import SEARCH_VISIBILITY_CHOICES, PROFILE_VISIBILITY_CHOICES

        choices_data = {
            "search_visibility": [
                {"value": choice[0], "display_name": choice[1]}
                for choice in SEARCH_VISIBILITY_CHOICES
            ],
            "profile_visibility": [
                {"value": choice[0], "display_name": choice[1]}
                for choice in PROFILE_VISIBILITY_CHOICES
            ],
        }

        return Response(choices_data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="Authorization",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=False,
            description="Bearer token (not required for email verification).",
        ),
    ],
)
class EmailVerificationView(UsersAppBaseAPIView):
    """
    Handles email verification after registration.

    This view verifies the signed token received via the verification email link.
    If the token is valid and not expired, it decodes the user data and creates the user account.

    - Expects a 'token' in the query params.
    - The token is signed and base64-encoded JSON.
    - Token is valid for 1 hour (3600 seconds).
    - If the email is already registered, it returns an error.
    - On success, it creates the user and marks the account as active.
    """

    permission_classes = []

    @extend_schema(
        summary="Verify email address",
        description="Verify a user's email address using the token sent in the verification email. The token is valid for 1 hour.",
        parameters=[
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Verification token from email",
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Email verified successfully",
                response=inline_serializer(
                    name="EmailVerificationSuccess",
                    fields={"message": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"message": "Email verified and account created."},
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Verification failed",
                response=inline_serializer(
                    name="EmailVerificationError",
                    fields={"error": serializers.CharField()},
                ),
                examples=[
                    OpenApiExample("Missing Token", value={"error": "Missing token"}),
                    OpenApiExample(
                        "Invalid Token", value={"error": "Invalid or expired token."}
                    ),
                    OpenApiExample(
                        "User Exists", value={"error": "User already exists."}
                    ),
                ],
            ),
        },
        tags=["Users"],
    )
    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response(
                {"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST
            )

        signer = TimestampSigner()
        try:
            # Step 1: verify the signature
            unsigned = signer.unsign(token, max_age=3600)

            # Step 2: base64 decode the payload
            json_payload = base64.urlsafe_b64decode(unsigned.encode()).decode()

            # Step 3: load JSON
            data = json.loads(json_payload)

            if User.objects.filter(email=data["email"]).exists():
                return Response(
                    {"error": "User already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.create_user(
                email=data["email"],
                username=data["username"],
                password=data["password"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                is_active=True,
            )
            return Response({"message": "Email verified and account created."})

        except (BadSignature, SignatureExpired):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
