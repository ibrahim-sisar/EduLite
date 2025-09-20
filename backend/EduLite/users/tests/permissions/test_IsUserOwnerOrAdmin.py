# users/tests/permissions/test_IsUserOwnerOrAdmin.py - Tests for IsUserOwnerOrAdmin permission

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

from ...permissions import IsUserOwnerOrAdmin


class IsUserOwnerOrAdminTest(TestCase):
    """Test cases for IsUserOwnerOrAdmin permission class."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = IsUserOwnerOrAdmin()

        # Create test users
        self.user = User.objects.create_user(
            username="target_user", email="user@example.com"
        )
        self.other_user = User.objects.create_user(
            username="other_user", email="other@example.com"
        )
        self.admin_user = User.objects.create_user(
            username="admin_user", email="admin@example.com", is_staff=True
        )
        self.superuser = User.objects.create_user(
            username="superuser", email="super@example.com", is_superuser=True
        )

        # Mock view for testing
        self.mock_view = type("MockView", (), {})()

    # --- has_permission Tests ---

    def test_has_permission_authenticated_user(self):
        """Test that authenticated users pass has_permission check."""
        request = self.factory.get("/")
        request.user = self.user

        result = self.permission.has_permission(request, self.mock_view)
        self.assertTrue(result)

    def test_has_permission_unauthenticated_user(self):
        """Test that unauthenticated users fail has_permission check."""
        request = self.factory.get("/")
        request.user = None

        result = self.permission.has_permission(request, self.mock_view)
        self.assertFalse(result)

    def test_has_permission_anonymous_user(self):
        """Test that anonymous users fail has_permission check."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/")
        request.user = AnonymousUser()

        result = self.permission.has_permission(request, self.mock_view)
        self.assertFalse(result)

    # --- has_object_permission Tests (Admin Users) ---

    def test_has_object_permission_admin_can_do_anything(self):
        """Test that admin users can perform any action on any User."""
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]

        for method in unsafe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.admin_user

                result = self.permission.has_object_permission(
                    request, self.mock_view, self.user
                )
                self.assertTrue(result, f"Admin should be able to {method} any user")

    def test_has_object_permission_admin_can_read_any_user(self):
        """Test that admin users can read any User."""
        request = self.factory.get("/")
        request.user = self.admin_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    # --- has_object_permission Tests (Safe Methods) ---

    def test_has_object_permission_safe_methods_any_user(self):
        """Test that any authenticated user can read any User with safe methods."""
        safe_methods = ["GET", "HEAD", "OPTIONS"]

        for method in safe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.other_user

                result = self.permission.has_object_permission(
                    request, self.mock_view, self.user
                )
                self.assertTrue(
                    result, f"{method} should be allowed for any authenticated user"
                )

    def test_has_object_permission_owner_can_read_own_record(self):
        """Test that users can read their own User record."""
        request = self.factory.get("/")
        request.user = self.user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    # --- has_object_permission Tests (Unsafe Methods - Owner) ---

    def test_has_object_permission_owner_can_update_own_record(self):
        """Test that users can update their own User record."""
        request = self.factory.put("/")
        request.user = self.user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    def test_has_object_permission_owner_can_patch_own_record(self):
        """Test that users can patch their own User record."""
        request = self.factory.patch("/")
        request.user = self.user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    def test_has_object_permission_owner_can_delete_own_record(self):
        """Test that users can delete their own User record."""
        request = self.factory.delete("/")
        request.user = self.user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    # --- has_object_permission Tests (Unsafe Methods - Other Users) ---

    def test_has_object_permission_other_user_cannot_update(self):
        """Test that users cannot update other users' records."""
        request = self.factory.put("/")
        request.user = self.other_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertFalse(result)

    def test_has_object_permission_other_user_cannot_patch(self):
        """Test that users cannot patch other users' records."""
        request = self.factory.patch("/")
        request.user = self.other_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertFalse(result)

    def test_has_object_permission_other_user_cannot_delete(self):
        """Test that users cannot delete other users' records."""
        request = self.factory.delete("/")
        request.user = self.other_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertFalse(result)

    def test_has_object_permission_other_user_cannot_post(self):
        """Test that users cannot POST to other users' records."""
        request = self.factory.post("/")
        request.user = self.other_user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertFalse(result)

    # --- Superuser Tests ---

    def test_has_object_permission_superuser_without_staff(self):
        """Test that superuser without is_staff still can't perform admin actions."""
        # Note: Current implementation only checks is_staff, not is_superuser
        request = self.factory.delete("/")
        request.user = self.superuser

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        # This might be unexpected behavior - superuser should probably have admin rights
        self.assertFalse(result)

    def test_has_object_permission_staff_and_superuser(self):
        """Test user who is both staff and superuser."""
        staff_super = User.objects.create_user(
            username="staff_super",
            email="staffsuper@example.com",
            is_staff=True,
            is_superuser=True,
        )

        request = self.factory.delete("/")
        request.user = staff_super

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    # --- Edge Cases ---

    def test_has_object_permission_user_identity_check(self):
        """Test that permission correctly identifies user identity."""
        # Test with same user object
        request = self.factory.put("/")
        request.user = self.user

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

        # Test with different user object but same ID (shouldn't happen in practice)
        user_copy = User.objects.get(id=self.user.id)
        request.user = user_copy

        result = self.permission.has_object_permission(
            request, self.mock_view, self.user
        )
        self.assertTrue(result)

    def test_has_object_permission_inactive_user(self):
        """Test permissions for inactive users."""
        inactive_user = User.objects.create_user(
            username="inactive", email="inactive@example.com", is_active=False
        )

        # Inactive user trying to modify their own record
        request = self.factory.put("/")
        request.user = inactive_user

        result = self.permission.has_object_permission(
            request, self.mock_view, inactive_user
        )
        # Permission should still work - is_active doesn't affect permission logic
        self.assertTrue(result)

    def test_has_object_permission_with_different_user_types(self):
        """Test permission with different combinations of user types."""
        test_cases = [
            # (requesting_user_type, target_user_type, method, expected)
            ("regular", "regular_other", "PUT", False),
            ("regular", "admin", "PUT", False),
            ("regular", "superuser", "PUT", False),
            ("admin", "regular", "PUT", True),
            ("admin", "admin_other", "PUT", True),
            ("admin", "superuser", "PUT", True),
        ]

        # Create additional users for testing
        regular_other = User.objects.create_user(username="regular_other")
        admin_other = User.objects.create_user(username="admin_other", is_staff=True)

        user_map = {
            "regular": self.user,
            "regular_other": regular_other,
            "admin": self.admin_user,
            "admin_other": admin_other,
            "superuser": self.superuser,
        }

        for req_type, target_type, method, expected in test_cases:
            with self.subTest(requesting=req_type, target=target_type, method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = user_map[req_type]

                result = self.permission.has_object_permission(
                    request, self.mock_view, user_map[target_type]
                )
                self.assertEqual(
                    result,
                    expected,
                    f"{req_type} {method} on {target_type} should be {expected}",
                )

    # --- Integration Tests ---

    def test_permission_class_inheritance(self):
        """Test that the permission class properly inherits from BasePermission."""
        self.assertIsInstance(self.permission, permissions.BasePermission)

    def test_permission_class_has_required_methods(self):
        """Test that the permission class has required methods."""
        self.assertTrue(hasattr(self.permission, "has_permission"))
        self.assertTrue(hasattr(self.permission, "has_object_permission"))
        self.assertTrue(callable(self.permission.has_permission))
        self.assertTrue(callable(self.permission.has_object_permission))
