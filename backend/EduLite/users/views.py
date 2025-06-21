# users/views.py
import logging

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination  # For list views
from rest_framework.permissions import IsAuthenticated

from .models import UserProfile, ProfileFriendRequest, UserProfilePrivacySettings
from .serializers import (
    UserSerializer,
    GroupSerializer,
    UserRegistrationSerializer,
    ProfileSerializer,
    ProfileFriendRequestSerializer,
    UserProfilePrivacySettingsSerializer
)
from .permissions import (
    IsProfileOwnerOrAdmin,
    IsUserOwnerOrAdmin,
    IsAdminUserOrReadOnly,
    IsFriendRequestReceiver,
    IsFriendRequestReceiverOrSender,
)

logger = logging.getLogger(__name__)

# --- Base API View for users App ---
class UsersAppBaseAPIView(APIView):
    """
    A custom base API view for the EduLite project.
    Provides default authentication permissions and a helper method to get serializer context.
    Other common functionalities for EduLite APIViews can be added here.

    **attribute** 'permission_classes' is set to [permissions.IsAuthenticated] by default.

    **method** 'get_serializer_context' is used to get the request object.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Ensures that the request object is available to the serializer context.
        This is useful for HATEOAS link generation or other context-aware serialization.
        """
        return {"request": self.request}


# --- User API Views ---


class UserListView(UsersAppBaseAPIView):
    """
    API view to list all users (with pagination).
    - GET: Returns a paginated list of users.
    """

    queryset_all = User.objects.all().order_by("-date_joined")
    serializer_class_instance = UserSerializer
    pagination_class_instance = PageNumberPagination
    pagination_class_instance.page_size = 10

    def get(self, request, *args, **kwargs):  # Handles LIST
        users = self.queryset_all

        paginator = self.pagination_class_instance()
        page = paginator.paginate_queryset(users, request, view=self)

        if page is not None:
            serializer = self.serializer_class_instance(
                page, many=True, context=self.get_serializer_context()
            )
            return paginator.get_paginated_response(serializer.data)

        # When pagination is not active or applicable, just return the full list
        serializer = self.serializer_class_instance(
            users, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class UserRegistrationView(UsersAppBaseAPIView):
    """
    API view to register a new user.
    - POST: Creates a new user.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):  # Handles CREATE
        serializer = UserRegistrationSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            user = serializer.save()  # Calls create() in the serializer
            return Response(
                {
                    "message": "User created successfully.",
                    "user_id": user.id,
                    "username": user.username,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(UsersAppBaseAPIView):
    """
    API view to retrieve, update, or delete a specific user by their PK.
    - GET: Retrieves a user.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset_all = User.objects.all()  # Base queryset for object lookup
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        return get_object_or_404(self.queryset_all, pk=pk)

    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class UserUpdateDeleteView(UsersAppBaseAPIView):
    """
    API view to update or delete a specific user by their PK.
    Inherits from UsersAppBaseAPIView.
    - PUT: Updates a user.
    - PATCH: Partially updates a user.
    - DELETE: Deletes a user.
    """

    permission_classes = [IsUserOwnerOrAdmin]
    queryset_all = User.objects.all()  # Base queryset for object lookup
    serializer_class_instance = UserSerializer

    def get_object(self, pk):
        """
        Helper method to retrieve the user object or raise a 404 error.
        """
        obj = get_object_or_404(self.queryset_all, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):  # Handles PARTIAL_UPDATE
        user = self.get_object(pk)
        serializer = self.serializer_class_instance(
            user, data=request.data, partial=True, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):  # Handles DESTROY
        user = self.get_object(pk)
        # Consider any pre-delete logic or checks here
        user.delete()
        return Response(
            {"message": "User deleted successfully."}, status=status.HTTP_202_ACCEPTED
        )


# --- Group API Views ---


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

    def post(self, request, *args, **kwargs):  # Handles CREATE
        serializer = self.serializer_class_instance(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        group = self.get_object(pk)
        serializer = self.serializer_class_instance(
            group, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def delete(self, request, pk, *args, **kwargs):  # Handles DESTROY
        group = self.get_object(pk)
        group.delete()
        return Response(
            {"message": "Group deleted successfully."}, status=status.HTTP_202_ACCEPTED
        )


# -- User Profile API Views -- ##


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

    def get(self, request, pk, *args, **kwargs):  # Handles RETRIEVE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):  # Handles UPDATE
        profile = self.get_object(pk)
        serializer = self.serializer_class_instance(
            profile, data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class UserSearchView(UsersAppBaseAPIView):
    """
    API view to search for users by username, first name, or last name.
    Accepts a query parameter 'q'.
    - GET: Returns a paginated list of matching active users with privacy controls.
    """

    serializer_class_instance = UserSerializer
    pagination_class_instance = PageNumberPagination

    def get(self, request, *args, **kwargs):
        from .logic.user_search_logic import execute_user_search

        search_query = request.query_params.get("q", "").strip()
        requesting_user = request.user if request.user.is_authenticated else None

        # Check if admin should bypass privacy filters
        bypass_privacy = requesting_user and requesting_user.is_superuser

        if not bypass_privacy:
            bypass_privacy = False

        # Execute the search with privacy controls using logic functions
        success, queryset, paginator, error_response = execute_user_search(
            search_query=search_query,
            requesting_user=requesting_user,
            request=request,
            view_instance=self,
            min_query_length=2,
            page_size=10,
            bypass_privacy_filters=bypass_privacy
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


class AcceptFriendRequestView(UsersAppBaseAPIView):
    """
    API view to accept a friend request.
    - POST: Accepts a friend request.
    """

    permission_classes = [IsAuthenticated, IsFriendRequestReceiver]

    def post(self, request, request_pk, *args, **kwargs):
        friend_request = get_object_or_404(ProfileFriendRequest, pk=request_pk)

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


class DeclineFriendRequestView(UsersAppBaseAPIView):
    """
    API view to decline or cancel a friend request.
    - POST: Declines/Cancels a specific friend request identified by request_pk.
    """

    permission_classes = [IsAuthenticated, IsFriendRequestReceiverOrSender]

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
        direction = request.query_params.get("direction", "received").lower()

        if direction == "sent":
            # Get requests sent by the user
            queryset = user_profile.sent_friend_requests.all()
        elif direction == "received":
            # Get requests received by the user
            queryset = user_profile.received_friend_requests.all()
        else:
            # Invalid direction parameter, return empty queryset or raise error
            return ProfileFriendRequest.objects.none()

        # Pre-fetch related user details for sender/receiver to optimize
        queryset = queryset.select_related("sender__user", "receiver__user")
        return queryset.order_by("-created_at")  # Ensure consistent ordering

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


class SendFriendRequestView(UsersAppBaseAPIView):
    """
    API view to send a new friend request.
    - POST: Creates a new ProfileFriendRequest.
    """

    # permission_classes is inherited from UsersAppBaseAPIView ([IsAuthenticated])

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
                message=message if message else None
            )
            return Response(
                {
                    "detail": "Friend request sent successfully.",
                    "request_id": friend_request.id
                },
                status=status.HTTP_201_CREATED
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
                self.request.user.username
            )

        return privacy_settings

    def get(self, request, *args, **kwargs):
        """
        Retrieve the current user's privacy settings.
        """
        privacy_settings = self.get_object()
        serializer = self.serializer_class_instance(
            privacy_settings, context=self.get_serializer_context()
        )
        return Response(serializer.data)

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


class UserProfilePrivacySettingsChoicesView(UsersAppBaseAPIView):
    """
    API view to get available privacy setting choices.
    - GET: Returns the available choices for privacy settings fields.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return available choices for privacy settings.
        """
        from .models import SEARCH_VISIBILITY_CHOICES, PROFILE_VISIBILITY_CHOICES

        choices_data = {
            "search_visibility_choices": [
                {"value": choice[0], "label": choice[1]}
                for choice in SEARCH_VISIBILITY_CHOICES
            ],
            "profile_visibility_choices": [
                {"value": choice[0], "label": choice[1]}
                for choice in PROFILE_VISIBILITY_CHOICES
            ],
        }

        return Response(choices_data)
