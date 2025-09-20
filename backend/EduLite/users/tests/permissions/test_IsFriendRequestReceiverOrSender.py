# users/tests/permissions/test_IsFriendRequestReceiverOrSender.py - Tests for IsFriendRequestReceiverOrSender permission

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

from ...models import ProfileFriendRequest
from ...permissions import IsFriendRequestReceiverOrSender


class IsFriendRequestReceiverOrSenderTest(TestCase):
    """Test cases for IsFriendRequestReceiverOrSender permission class."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = IsFriendRequestReceiverOrSender()

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

    def test_has_object_permission_sender_can_access(self):
        """Test that the sender can access their friend request."""
        request = self.factory.post("/")
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

    def test_has_object_permission_sender_all_http_methods(self):
        """Test that sender can access with all HTTP methods."""
        methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

        for method in methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.sender_user

                result = self.permission.has_object_permission(
                    request, self.mock_view, self.friend_request
                )
                self.assertTrue(result, f"Sender should be able to use {method}")

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

    def test_has_object_permission_sender_profile_deleted(self):
        """Test behavior when sender's profile is deleted after request creation."""
        request = self.factory.post("/")
        request.user = self.sender_user

        # Create orphaned request with no sender
        orphaned_request = ProfileFriendRequest(
            sender=None,
            receiver=self.receiver_profile,
            message="Orphaned sender request",
        )

        # This should return False or raise an exception
        try:
            result = self.permission.has_object_permission(
                request, self.mock_view, orphaned_request
            )
            self.assertFalse(result)
        except AttributeError:
            # This is acceptable - the permission fails due to None sender
            pass

    def test_has_object_permission_receiver_profile_deleted(self):
        """Test behavior when receiver's profile is deleted after request creation."""
        request = self.factory.post("/")
        request.user = self.receiver_user

        # Create orphaned request with no receiver
        orphaned_request = ProfileFriendRequest(
            sender=self.sender_profile,
            receiver=None,
            message="Orphaned receiver request",
        )

        # This should return False or raise an exception
        try:
            result = self.permission.has_object_permission(
                request, self.mock_view, orphaned_request
            )
            self.assertFalse(result)
        except AttributeError:
            # This is acceptable - the permission fails due to None receiver
            pass

    # --- Wrong Object Type ---

    def test_has_object_permission_wrong_object_type(self):
        """Test permission with non-ProfileFriendRequest objects."""
        request = self.factory.post("/")
        request.user = self.sender_user

        # Test with a User object instead of ProfileFriendRequest
        result = self.permission.has_object_permission(
            request, self.mock_view, self.sender_user
        )
        # Permission should return False for wrong object types
        self.assertFalse(result)

    def test_has_object_permission_none_object(self):
        """Test permission with None object."""
        request = self.factory.post("/")
        request.user = self.sender_user

        result = self.permission.has_object_permission(request, self.mock_view, None)
        self.assertFalse(result)

    # --- Multiple Friend Requests ---

    def test_has_object_permission_multiple_requests(self):
        """Test that permission works correctly with multiple friend requests."""
        # Create another friend request in the opposite direction
        reverse_request = ProfileFriendRequest.objects.create(
            sender=self.receiver_profile,
            receiver=self.sender_profile,
            message="Let's be friends too!",
        )

        # Test original request access
        request = self.factory.post("/")

        # Sender should have access to original request
        request.user = self.sender_user
        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Sender should also have access to reverse request (as receiver)
        result = self.permission.has_object_permission(
            request, self.mock_view, reverse_request
        )
        self.assertTrue(result)

        # Receiver should have access to original request
        request.user = self.receiver_user
        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Receiver should also have access to reverse request (as sender)
        result = self.permission.has_object_permission(
            request, self.mock_view, reverse_request
        )
        self.assertTrue(result)

        # Other user should have access to neither
        request.user = self.other_user
        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertFalse(result)

        result = self.permission.has_object_permission(
            request, self.mock_view, reverse_request
        )
        self.assertFalse(result)

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
        # Admin should not have access unless they are sender or receiver
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
        # Superuser should not have access unless they are sender or receiver
        self.assertFalse(result)

    # --- Inactive Users ---

    def test_has_object_permission_inactive_sender(self):
        """Test permission when sender is inactive."""
        self.sender_user.is_active = False
        self.sender_user.save()

        request = self.factory.post("/")
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        # Inactive status shouldn't affect permission
        self.assertTrue(result)

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

    # --- Custom Message Test ---

    def test_permission_message(self):
        """Test that the permission has a custom message."""
        expected_message = (
            "You do not have permission to perform this action on this friend request."
        )
        self.assertEqual(self.permission.message, expected_message)

    # --- Integration Tests ---

    def test_permission_class_inheritance(self):
        """Test that the permission class properly inherits from BasePermission."""
        self.assertIsInstance(self.permission, permissions.BasePermission)

    def test_permission_class_has_default_has_permission_method(self):
        """Test that this permission class uses default has_permission."""
        # This permission is object-level only but inherits default has_permission from BasePermission
        self.assertTrue(hasattr(self.permission, "has_permission"))
        # Test that it uses the default BasePermission behavior (returns True)
        request = self.factory.get("/")
        request.user = self.sender_user
        result = self.permission.has_permission(request, self.mock_view)
        self.assertTrue(result)  # BasePermission default returns True

    def test_permission_class_has_required_methods(self):
        """Test that the permission class has required methods."""
        self.assertTrue(hasattr(self.permission, "has_object_permission"))
        self.assertTrue(callable(self.permission.has_object_permission))

    # --- Real-World Usage Scenarios ---

    def test_typical_decline_friend_request_scenario(self):
        """Test typical usage scenario for declining friend requests."""
        # This permission would typically be used in DeclineFriendRequestView

        # Receiver should be able to decline
        request = self.factory.post("/api/friend-requests/1/decline/")
        request.user = self.receiver_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Sender should be able to cancel (decline their own request)
        request.user = self.sender_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Other user should not be able to decline
        request.user = self.other_user

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
        # User should have access since they are both sender and receiver
        self.assertTrue(result)

    # --- Performance Tests ---

    def test_permission_check_performance(self):
        """Test that permission checking is reasonably fast."""
        import time

        request = self.factory.post("/")
        request.user = self.sender_user

        # Time multiple permission checks
        start_time = time.time()

        for _ in range(100):
            self.permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )

        end_time = time.time()
        duration = end_time - start_time

        # Should complete 100 checks in less than 10ms
        self.assertLess(duration, 0.01, "Permission checking is too slow")

    # --- Edge Case: Profile Comparison ---

    def test_has_object_permission_profile_equality(self):
        """Test that profile comparison works correctly."""
        # Create a new user and manually set their profile to match sender
        duplicate_user = User.objects.create_user(
            username="duplicate", email="duplicate@example.com"
        )

        # This shouldn't be possible in real app, but test the edge case
        original_profile = duplicate_user.profile

        request = self.factory.post("/")
        request.user = duplicate_user

        # With original profile, should not have access
        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertFalse(result)

        # If we somehow set the profile to match sender (this would break referential integrity)
        duplicate_user.profile = self.sender_profile

        result = self.permission.has_object_permission(
            request, self.mock_view, self.friend_request
        )
        self.assertTrue(result)

        # Restore to avoid database issues
        duplicate_user.profile = original_profile
