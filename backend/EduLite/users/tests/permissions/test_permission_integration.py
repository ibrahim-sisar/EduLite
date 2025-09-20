# users/tests/permissions/test_permission_integration.py - Integration tests for permission interactions

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

from ...models import UserProfile, ProfileFriendRequest
from ...permissions import (
    IsProfileOwnerOrAdmin,
    IsUserOwnerOrAdmin,
    IsAdminUserOrReadOnly,
    IsFriendRequestReceiver,
    IsFriendRequestReceiverOrSender,
)


class PermissionIntegrationTest(TestCase):
    """Test cases for how permissions work together in real scenarios."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()

        # Create test users
        self.regular_user = User.objects.create_user(
            username="regular_user", email="regular@example.com"
        )
        self.other_user = User.objects.create_user(
            username="other_user", email="other@example.com"
        )
        self.admin_user = User.objects.create_user(
            username="admin_user", email="admin@example.com", is_staff=True
        )

        # Get profiles
        self.regular_profile = self.regular_user.profile
        self.other_profile = self.other_user.profile
        self.admin_profile = self.admin_user.profile

        # Create friend request
        self.friend_request = ProfileFriendRequest.objects.create(
            sender=self.regular_profile,
            receiver=self.other_profile,
            message="Let's be friends!",
        )

        # Permission instances
        self.profile_owner_permission = IsProfileOwnerOrAdmin()
        self.user_owner_permission = IsUserOwnerOrAdmin()
        self.admin_permission = IsAdminUserOrReadOnly()
        self.receiver_permission = IsFriendRequestReceiver()
        self.receiver_or_sender_permission = IsFriendRequestReceiverOrSender()

        # Mock view
        self.mock_view = type("MockView", (), {})()

    # --- Profile Management Scenarios ---

    def test_profile_access_control_flow(self):
        """Test complete profile access control flow."""
        # Regular user accessing their own profile
        request = self.factory.get("/")
        request.user = self.regular_user

        # Should pass has_permission check
        self.assertTrue(
            self.profile_owner_permission.has_permission(request, self.mock_view)
        )

        # Should pass has_object_permission for their own profile
        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_profile
            )
        )

        # Should fail has_object_permission for other's profile with unsafe method
        request = self.factory.put("/")
        request.user = self.regular_user

        self.assertFalse(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.other_profile
            )
        )

        # Admin should be able to access any profile
        request.user = self.admin_user

        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.other_profile
            )
        )

    def test_user_profile_consistency(self):
        """Test that User and UserProfile permissions are consistent."""
        request = self.factory.put("/")
        request.user = self.regular_user

        # User should be able to update their own User record
        user_permission_result = self.user_owner_permission.has_object_permission(
            request, self.mock_view, self.regular_user
        )

        # User should be able to update their own profile
        profile_permission_result = self.profile_owner_permission.has_object_permission(
            request, self.mock_view, self.regular_profile
        )

        # Both should be True for consistency
        self.assertTrue(user_permission_result)
        self.assertTrue(profile_permission_result)

        # Test with other user's data
        user_permission_result = self.user_owner_permission.has_object_permission(
            request, self.mock_view, self.other_user
        )

        profile_permission_result = self.profile_owner_permission.has_object_permission(
            request, self.mock_view, self.other_profile
        )

        # Both should be False for consistency
        self.assertFalse(user_permission_result)
        self.assertFalse(profile_permission_result)

    # --- Admin Permission Scenarios ---

    def test_admin_override_behavior(self):
        """Test that admin permissions properly override other restrictions."""
        request = self.factory.delete("/")
        request.user = self.admin_user

        # Admin should be able to delete any user
        self.assertTrue(
            self.user_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_user
            )
        )

        # Admin should be able to modify any profile
        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_profile
            )
        )

        # Admin should be able to use admin-only endpoints
        self.assertTrue(self.admin_permission.has_permission(request, self.mock_view))

        # But admin should NOT have special privileges for friend requests
        self.assertFalse(
            self.receiver_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

    # --- Friend Request Permission Scenarios ---

    def test_friend_request_permission_specificity(self):
        """Test that friend request permissions are more specific than general permissions."""
        request = self.factory.post("/")

        # Receiver should be able to accept
        request.user = self.other_user

        self.assertTrue(
            self.receiver_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        self.assertTrue(
            self.receiver_or_sender_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        # Sender should only be able to use ReceiverOrSender permission
        request.user = self.regular_user

        self.assertFalse(
            self.receiver_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        self.assertTrue(
            self.receiver_or_sender_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        # Admin should not have special access to friend requests
        request.user = self.admin_user

        self.assertFalse(
            self.receiver_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        self.assertFalse(
            self.receiver_or_sender_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

    # --- Multiple Permission Combination Tests ---

    def test_combined_permission_logic(self):
        """Test how multiple permissions would work together in a view."""
        # Simulate a view that requires both IsAuthenticated and IsProfileOwnerOrAdmin
        request = self.factory.put("/")
        request.user = self.regular_user

        # Step 1: Check if user is authenticated (IsAuthenticated would handle this)
        is_authenticated = request.user.is_authenticated
        self.assertTrue(is_authenticated)

        # Step 2: Check profile ownership
        has_profile_permission = self.profile_owner_permission.has_permission(
            request, self.mock_view
        )
        self.assertTrue(has_profile_permission)

        # Step 3: Check object-level permission
        has_object_permission = self.profile_owner_permission.has_object_permission(
            request, self.mock_view, self.regular_profile
        )
        self.assertTrue(has_object_permission)

        # Combined result
        final_permission = (
            is_authenticated and has_profile_permission and has_object_permission
        )
        self.assertTrue(final_permission)

        # Test failure case
        has_object_permission = self.profile_owner_permission.has_object_permission(
            request, self.mock_view, self.other_profile
        )
        self.assertFalse(has_object_permission)

        final_permission = (
            is_authenticated and has_profile_permission and has_object_permission
        )
        self.assertFalse(final_permission)

    # --- Edge Case Interactions ---

    def test_permission_with_inactive_users(self):
        """Test permission interactions with inactive users."""
        # Make regular user inactive
        self.regular_user.is_active = False
        self.regular_user.save()

        request = self.factory.get("/")
        request.user = self.regular_user

        # User should still pass basic permission checks
        # (is_active is typically checked by authentication, not permissions)
        self.assertTrue(
            self.profile_owner_permission.has_permission(request, self.mock_view)
        )

        self.assertTrue(
            self.user_owner_permission.has_permission(request, self.mock_view)
        )

        # Object-level permissions should still work
        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_profile
            )
        )

    def test_permission_cascade_effects(self):
        """Test how changes in user status affect multiple permissions."""
        request = self.factory.post("/")
        request.user = self.regular_user

        # Initially regular user
        get_request = self.factory.get("/")
        get_request.user = self.regular_user
        self.assertTrue(
            self.admin_permission.has_permission(get_request, self.mock_view)
        )  # Can read

        self.assertFalse(
            self.admin_permission.has_permission(request, self.mock_view)
        )  # Cannot write

        # Make user admin
        self.regular_user.is_staff = True
        self.regular_user.save()

        # Now should be able to write
        self.assertTrue(self.admin_permission.has_permission(request, self.mock_view))

        # Should still be able to access their own data
        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_profile
            )
        )

        # Should now be able to access other users' data
        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.other_profile
            )
        )

    # --- Performance Tests ---

    def test_permission_check_performance(self):
        """Test that multiple permission checks don't degrade performance."""
        import time

        request = self.factory.get("/")
        request.user = self.regular_user

        permissions_to_test = [
            (
                self.profile_owner_permission,
                "has_permission",
                [request, self.mock_view],
            ),
            (self.user_owner_permission, "has_permission", [request, self.mock_view]),
            (self.admin_permission, "has_permission", [request, self.mock_view]),
            (
                self.profile_owner_permission,
                "has_object_permission",
                [request, self.mock_view, self.regular_profile],
            ),
            (
                self.user_owner_permission,
                "has_object_permission",
                [request, self.mock_view, self.regular_user],
            ),
        ]

        start_time = time.time()

        # Run each permission check 50 times
        for _ in range(50):
            for permission, method_name, args in permissions_to_test:
                method = getattr(permission, method_name)
                method(*args)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete 250 permission checks in less than 50ms
        self.assertLess(duration, 0.05, "Permission checking is too slow")

    # --- Real-World Scenario Tests ---

    def test_user_profile_update_scenario(self):
        """Test complete user profile update scenario."""
        # User wants to update their profile
        request = self.factory.patch("/api/profiles/1/")
        request.user = self.regular_user

        # Check authentication (would be handled by IsAuthenticated)
        self.assertTrue(request.user.is_authenticated)

        # Check general permission
        self.assertTrue(
            self.profile_owner_permission.has_permission(request, self.mock_view)
        )

        # Check object-level permission
        self.assertTrue(
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_profile
            )
        )

        # All checks pass - user can update their profile

    def test_admin_user_management_scenario(self):
        """Test admin managing users scenario."""
        # Admin wants to delete a user
        request = self.factory.delete("/api/users/1/")
        request.user = self.admin_user

        # Check if user can access admin-only endpoint
        self.assertTrue(self.admin_permission.has_permission(request, self.mock_view))

        # Check if user can delete this specific user
        self.assertTrue(
            self.user_owner_permission.has_object_permission(
                request, self.mock_view, self.regular_user
            )
        )

        # All checks pass - admin can delete the user

    def test_friend_request_workflow_scenario(self):
        """Test complete friend request workflow."""
        # Sender wants to cancel their request
        request = self.factory.delete("/api/friend-requests/1/")
        request.user = self.regular_user  # Sender

        # Only ReceiverOrSender permission should allow this
        self.assertTrue(
            self.receiver_or_sender_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        # Receiver wants to accept the request
        request.user = self.other_user  # Receiver

        # Both Receiver and ReceiverOrSender permissions should allow this
        self.assertTrue(
            self.receiver_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

        self.assertTrue(
            self.receiver_or_sender_permission.has_object_permission(
                request, self.mock_view, self.friend_request
            )
        )

    # --- Error Handling Integration ---

    def test_permission_error_consistency(self):
        """Test that permissions handle errors consistently."""
        request = self.factory.post("/")
        request.user = None  # Unauthenticated

        # All permission classes should handle unauthenticated users consistently
        self.assertFalse(
            self.profile_owner_permission.has_permission(request, self.mock_view)
        )

        self.assertFalse(
            self.user_owner_permission.has_permission(request, self.mock_view)
        )

        self.assertFalse(self.admin_permission.has_permission(request, self.mock_view))

        # Object-level permissions with invalid objects
        with self.assertRaises((AttributeError, ValueError)):
            self.profile_owner_permission.has_object_permission(
                request, self.mock_view, None
            )

    def test_permission_with_deleted_objects(self):
        """Test permissions when related objects are deleted."""
        # Note: In the current implementation, profiles are created via signals
        # and deleting them might cause cascading issues. This test demonstrates
        # the importance of proper error handling in permission classes.

        request = self.factory.get("/")
        request.user = self.regular_user

        # The profile should exist initially
        self.assertTrue(hasattr(self.regular_user, "profile"))

        # If a profile were deleted, permission classes should handle it gracefully
        # This is more of a documentation test showing the importance of defensive programming
