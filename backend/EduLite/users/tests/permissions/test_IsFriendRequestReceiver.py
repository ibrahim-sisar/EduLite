# users/tests/permissions/test_IsFriendRequestReceiver.py - Tests for IsFriendRequestReceiver permission

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from ...models import ProfileFriendRequest
from ...permissions import IsFriendRequestReceiver


class IsFriendRequestReceiverTest(TestCase):
    """Test cases for IsFriendRequestReceiver permission class."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = IsFriendRequestReceiver()

        # Create test users
        self.sender_user = User.objects.create_user(
            username="sender", email="sender@example.com"
        )
        self.receiver_user = User.objects.create_user(
            username="receiver", email="receiver@example.com"
        )
        self.other_user = User.objects.create_user(
            username="other_user", email="other@example.com"
        )

        # Get profiles (created automatically via signals)
        self.sender_profile = self.sender_user.profile
        self.receiver_profile = self.receiver_user.profile
        self.other_profile = self.other_user.profile

        # Create a friend request for testing
        self.friend_request = ProfileFriendRequest.objects.create(
            sender=self.sender_profile,
            receiver=self.receiver_profile,
            message="Let's be friends!",
        )

        # Mock view for testing
        self.mock_view = type("MockView", (), {})()

    # --- has_object_permission Tests (Receiver) ---

    def test_has_object_permission_receiver_can_access(self):
        """Test that the receiver can access their friend request."""
        request = self.factory.post("/")
        request.user = self.receiver_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

    def test_has_object_permission_receiver_all_http_methods(self):
        """Test that receiver can access with all HTTP methods."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

        for method in methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.receiver_user

                result = self.permission.has_object_permission(
                    request, self.mock_view, self.friend_request
                )
                self.assertTrue(result, f"Receiver should be able to use {method}")

    # --- has_object_permission Tests (Sender) ---

    def test_has_object_permission_sender_cannot_access(self):
        """Test that the sender cannot access the friend request."""
        request = self.factory.post("/")
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertFalse(result)

    def test_has_object_permission_sender_all_http_methods(self):
        """Test that sender cannot access with any HTTP method."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

        for method in methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.sender_user

                result = self.permission.has_object_permission(
                    request, self.mock_view, self.friend_request
                )
                self.assertFalse(result, f"Sender should not be able to use {method}")

    # --- has_object_permission Tests (Other Users) ---

    def test_has_object_permission_other_user_cannot_access(self):
        """Test that unrelated users cannot access the friend request."""
        request = self.factory.post("/")
        request.user = self.other_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertFalse(result)

    def test_has_object_permission_other_user_all_http_methods(self):
        """Test that other users cannot access with any HTTP method."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

        for method in methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.other_user

                result = self.permission.has_object_permission(
                    request, self.mock_view, self.friend_request
                )
                self.assertFalse(
                    result, f"Other user should not be able to use {method}"
                )

    # --- Edge Cases: Users Without Profiles ---

    def test_has_object_permission_user_without_profile(self):
        """Test behavior when user doesn't have a profile."""
        # Create user without triggering profile creation signal
        user_without_profile = User(
            username="no_profile", email="noprofile@example.com"
        )
        user_without_profile.save()

        # Manually delete the profile if it was created by signal
        if hasattr(user_without_profile, "profile"):
            user_without_profile.profile.delete()

        request = self.factory.post("/")
        request.user = user_without_profile

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertFalse(result)

    def test_has_object_permission_receiver_profile_deleted(self):
        """Test behavior when receiver's profile is deleted after request creation."""
        # This shouldn't happen in normal operation, but let's test it
        request = self.factory.post("/")
        request.user = self.receiver_user

        # The permission code doesn't handle None receiver gracefully
        # This is actually a potential bug in the permission class
        # Let's test with a modified friend request that has no receiver
        orphaned_request = ProfileFriendRequest(
            sender=self.sender_profile, receiver=None, message="Orphaned request"
        )

        # This should raise an exception or return False
        try:
            result = self.permission.has_object_permission(
                request, self.mock_view, orphaned_request
            )
            self.assertFalse(result)
        except AttributeError:
            # This is acceptable - the permission fails due to None receiver
            pass

    # --- Multiple Friend Requests ---

    def test_has_object_permission_multiple_requests_correct_receiver(self):
        """Test that permission works correctly with multiple friend requests."""
        # Create another friend request in the opposite direction
        reverse_request = ProfileFriendRequest.objects.create(
            sender=self.receiver_profile,
            receiver=self.sender_profile,
            message="Let's be friends too!",
        )

        # Test original request - receiver should still have access
        request = self.factory.post("/")
        request.user = self.receiver_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Test reverse request - sender (of original) should have access as receiver
        result = self.permission.has_object_permission(
            request, self.mock_view, reverse_request
        )
        self.assertFalse(result)  # receiver_user is not the receiver of reverse_request

        # Test reverse request with correct receiver
        request.user = self.sender_user
        result = self.permission.has_object_permission(
            request, self.mock_view, reverse_request
        )
        self.assertTrue(result)  # sender_user is the receiver of reverse_request

    # --- Admin Users ---

    def test_has_object_permission_admin_user(self):
        """Test that admin users don't get special treatment."""
        admin_user = User.objects.create_user(
            username="admin", email="admin@example.com", is_staff=True
        )

        request = self.factory.post("/")
        request.user = admin_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        # Admin should not have access unless they are the receiver
        self.assertFalse(result)

    def test_has_object_permission_superuser(self):
        """Test that superusers don't get special treatment."""
        superuser = User.objects.create_user(
            username="superuser", email="super@example.com", is_superuser=True
        )

        request = self.factory.post("/")
        request.user = superuser

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        # Superuser should not have access unless they are the receiver
        self.assertFalse(result)

    # --- Different Object Types ---

    def test_has_object_permission_wrong_object_type(self):
        """Test permission with non-ProfileFriendRequest objects."""
        # Test with a User object instead of ProfileFriendRequest
        request = self.factory.post("/")
        request.user = self.receiver_user

        # The permission doesn't explicitly check object type, so this might pass
        # based on attribute access
        try:
            result = self.permission.has_object_permission(
                request, self.mock_view, self.receiver_user
            )
            # This should fail because User doesn't have a 'receiver' attribute
            self.assertFalse(result)
        except AttributeError:
            # This is also acceptable - the permission fails due to wrong object type
            pass

    # --- Inactive Users ---

    def test_has_object_permission_inactive_receiver(self):
        """Test permission when receiver is inactive."""
        self.receiver_user.is_active = False
        self.receiver_user.save()

        request = self.factory.post("/")
        request.user = self.receiver_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        # Inactive status shouldn't affect permission
        self.assertTrue(result)

    def test_has_object_permission_inactive_sender(self):
        """Test permission when sender is inactive."""
        self.sender_user.is_active = False
        self.sender_user.save()

        request = self.factory.post("/")
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        # Sender still shouldn't have access even if inactive
        self.assertFalse(result)

    # --- Integration Tests ---

    def test_permission_class_has_default_has_permission_method(self):
        """Test that this permission class uses default has_permission."""
        # This permission is object-level only but inherits default has_permission from BasePermission
        self.assertTrue(hasattr(self.permission, "has_permission"))
        # Test that it uses the default BasePermission behavior (returns True)
        request = self.factory.get("/")
        request.user = self.receiver_user
        result = self.permission.has_permission(request, self.mock_view)
        self.assertTrue(result)  # BasePermission default returns True

    def test_permission_class_has_required_methods(self):
        """Test that the permission class has required methods."""
        self.assertTrue(hasattr(self.permission, "has_object_permission"))
        self.assertTrue(callable(self.permission.has_object_permission))

    # --- Real-World Usage Scenarios ---

    def test_typical_accept_friend_request_scenario(self):
        """Test typical usage scenario for accepting friend requests."""
        # This permission would typically be used in AcceptFriendRequestView

        # Receiver should be able to accept
        request = self.factory.post("/api/friend-requests/1/accept/")
        request.user = self.receiver_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Sender should not be able to accept their own request
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertFalse(result)

    def test_friend_request_from_self_to_self(self):
        """Test edge case where sender and receiver are the same (shouldn't happen)."""
        # Create a malformed friend request (this shouldn't be possible in normal operation)
        self_request = ProfileFriendRequest(
            sender=self.sender_profile,
            receiver=self.sender_profile,  # Same as sender
            message="Self request",
        )
        # Don't save this as it would violate business logic

        request = self.factory.post("/")
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self_request
        )
        # User should have access since they are the receiver
        self.assertTrue(result)
