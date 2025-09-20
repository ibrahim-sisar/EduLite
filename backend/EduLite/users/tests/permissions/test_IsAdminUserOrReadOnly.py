# users/tests/permissions/test_IsAdminUserOrReadOnly.py - Tests for IsAdminUserOrReadOnly permission

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import permissions

from ...permissions import IsAdminUserOrReadOnly


class IsAdminUserOrReadOnlyTest(TestCase):
    """Test cases for IsAdminUserOrReadOnly permission class."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = IsAdminUserOrReadOnly()

        # Create test users
        self.regular_user = User.objects.create_user(
            username="regular_user", email="regular@example.com"
        )
        self.admin_user = User.objects.create_user(
            username="admin_user", email="admin@example.com", is_staff=True
        )
        self.superuser = User.objects.create_user(
            username="superuser", email="super@example.com", is_superuser=True
        )
        self.staff_superuser = User.objects.create_user(
            username="staff_super",
            email="staffsuper@example.com",
            is_staff=True,
            is_superuser=True,
        )

        # Mock view for testing
        self.mock_view = type("MockView", (), {})()

    # --- has_permission Tests (Unauthenticated Users) ---

    def test_has_permission_unauthenticated_user(self):
        """Test that unauthenticated users are denied access."""
        request = self.factory.get("/")
        request.user = None

        result = self.permission.has_permission(request, self.mock_view)
        self.assertFalse(result)

    def test_has_permission_anonymous_user(self):
        """Test that anonymous users are denied access."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/")
        request.user = AnonymousUser()

        result = self.permission.has_permission(request, self.mock_view)
        self.assertFalse(result)

    # --- has_permission Tests (Safe Methods) ---

    def test_has_permission_safe_methods_regular_user(self):
        """Test that regular users can use safe methods."""
        safe_methods = ["GET", "HEAD", "OPTIONS"]

        for method in safe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.regular_user

                result = self.permission.has_permission(request, self.mock_view)
                self.assertTrue(result, f"Regular user should be able to {method}")

    def test_has_permission_safe_methods_admin_user(self):
        """Test that admin users can use safe methods."""
        safe_methods = ["GET", "HEAD", "OPTIONS"]

        for method in safe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.admin_user

                result = self.permission.has_permission(request, self.mock_view)
                self.assertTrue(result, f"Admin user should be able to {method}")

    def test_has_permission_safe_methods_superuser(self):
        """Test that superusers can use safe methods."""
        safe_methods = ["GET", "HEAD", "OPTIONS"]

        for method in safe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.superuser

                result = self.permission.has_permission(request, self.mock_view)
                self.assertTrue(result, f"Superuser should be able to {method}")

    # --- has_permission Tests (Unsafe Methods - Regular Users) ---

    def test_has_permission_unsafe_methods_regular_user_denied(self):
        """Test that regular users cannot use unsafe methods."""
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]

        for method in unsafe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.regular_user

                result = self.permission.has_permission(request, self.mock_view)
                self.assertFalse(result, f"Regular user should not be able to {method}")

    def test_has_permission_inactive_user_safe_methods(self):
        """Test that inactive regular users can still read."""
        inactive_user = User.objects.create_user(
            username="inactive", email="inactive@example.com", is_active=False
        )

        request = self.factory.get("/")
        request.user = inactive_user

        result = self.permission.has_permission(request, self.mock_view)
        self.assertTrue(result)

    def test_has_permission_inactive_user_unsafe_methods(self):
        """Test that inactive regular users cannot write."""
        inactive_user = User.objects.create_user(
            username="inactive", email="inactive@example.com", is_active=False
        )

        request = self.factory.post("/")
        request.user = inactive_user

        result = self.permission.has_permission(request, self.mock_view)
        self.assertFalse(result)

    # --- has_permission Tests (Unsafe Methods - Admin Users) ---

    def test_has_permission_unsafe_methods_admin_user_allowed(self):
        """Test that admin users can use unsafe methods."""
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]

        for method in unsafe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.admin_user

                result = self.permission.has_permission(request, self.mock_view)
                self.assertTrue(result, f"Admin user should be able to {method}")

    def test_has_permission_unsafe_methods_staff_superuser_allowed(self):
        """Test that staff+superuser can use unsafe methods."""
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]

        for method in unsafe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.staff_superuser

                result = self.permission.has_permission(request, self.mock_view)
                self.assertTrue(result, f"Staff+superuser should be able to {method}")

    def test_has_permission_inactive_admin_unsafe_methods(self):
        """Test that inactive admin users can still use unsafe methods."""
        inactive_admin = User.objects.create_user(
            username="inactive_admin",
            email="inactiveadmin@example.com",
            is_staff=True,
            is_active=False,
        )

        request = self.factory.post("/")
        request.user = inactive_admin

        result = self.permission.has_permission(request, self.mock_view)
        self.assertTrue(result)

    # --- Superuser Edge Cases ---

    def test_has_permission_superuser_without_staff_unsafe_methods(self):
        """Test that superuser without is_staff cannot use unsafe methods."""
        # Note: Current implementation only checks is_staff, not is_superuser
        unsafe_methods = ["POST", "PUT", "PATCH", "DELETE"]

        for method in unsafe_methods:
            with self.subTest(method=method):
                request = getattr(self.factory, method.lower())("/")
                request.user = self.superuser

                result = self.permission.has_permission(request, self.mock_view)
                # This might be unexpected behavior - superuser should probably have admin rights
                self.assertFalse(result, f"Superuser without staff cannot {method}")

    # --- Edge Cases and Boundary Tests ---

    def test_has_permission_user_with_mixed_permissions(self):
        """Test users with various permission combinations."""
        test_cases = [
            # (is_staff, is_superuser, is_active, method, expected)
            (True, False, True, "POST", True),  # Staff only
            (False, True, True, "POST", False),  # Superuser only (current behavior)
            (True, True, True, "POST", True),  # Both staff and superuser
            (True, False, False, "POST", True),  # Inactive staff
            (False, False, True, "POST", False),  # Regular user
            (False, False, False, "GET", True),  # Inactive regular user reading
        ]

        for is_staff, is_superuser, is_active, method, expected in test_cases:
            with self.subTest(
                staff=is_staff, super=is_superuser, active=is_active, method=method
            ):
                user = User.objects.create_user(
                    username=f"test_{is_staff}_{is_superuser}_{is_active}_{method}",
                    email=f"test_{is_staff}_{is_superuser}_{is_active}_{method}@example.com",
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    is_active=is_active,
                )

                request = getattr(self.factory, method.lower())("/")
                request.user = user

                result = self.permission.has_permission(request, self.mock_view)
                self.assertEqual(
                    result,
                    expected,
                    f"User(staff={is_staff}, super={is_superuser}, active={is_active}) "
                    f"{method} should be {expected}",
                )

    def test_has_permission_custom_http_methods(self):
        """Test permission with custom/uncommon HTTP methods."""
        # Some custom methods that might be used
        custom_safe_methods = ["HEAD", "OPTIONS"]  # These are in SAFE_METHODS
        custom_unsafe_methods = ["PATCH", "DELETE"]  # These are not in SAFE_METHODS

        for method in custom_safe_methods:
            request = self.factory.generic(method, "/")
            request.user = self.regular_user

            result = self.permission.has_permission(request, self.mock_view)
            self.assertTrue(result, f"Regular user should be able to use {method}")

        for method in custom_unsafe_methods:
            request = self.factory.generic(method, "/")
            request.user = self.regular_user

            result = self.permission.has_permission(request, self.mock_view)
            self.assertFalse(result, f"Regular user should not be able to use {method}")

    # --- Object-Level Permission Tests ---

    def test_no_custom_object_permission_method(self):
        """Test that this permission class doesn't override has_object_permission."""
        # This permission class only overrides has_permission, not has_object_permission
        # BasePermission provides a default has_object_permission that returns True
        self.assertTrue(hasattr(self.permission, "has_object_permission"))
        # Test that it uses the default BasePermission behavior
        request = self.factory.get("/")
        request.user = self.regular_user
        result = self.permission.has_object_permission(request, self.mock_view, None)
        self.assertTrue(result)  # BasePermission default returns True

    # --- Integration Tests ---

    def test_permission_class_inheritance(self):
        """Test that the permission class properly inherits from BasePermission."""
        self.assertIsInstance(self.permission, permissions.BasePermission)

    def test_permission_class_has_required_methods(self):
        """Test that the permission class has required methods."""
        self.assertTrue(hasattr(self.permission, "has_permission"))
        self.assertTrue(callable(self.permission.has_permission))

    def test_safe_methods_constant(self):
        """Test that safe methods are correctly identified."""
        # Verify that our understanding of SAFE_METHODS is correct
        self.assertIn("GET", permissions.SAFE_METHODS)
        self.assertIn("HEAD", permissions.SAFE_METHODS)
        self.assertIn("OPTIONS", permissions.SAFE_METHODS)
        self.assertNotIn("POST", permissions.SAFE_METHODS)
        self.assertNotIn("PUT", permissions.SAFE_METHODS)
        self.assertNotIn("PATCH", permissions.SAFE_METHODS)
        self.assertNotIn("DELETE", permissions.SAFE_METHODS)

    # --- Real-World Usage Scenarios ---

    def test_typical_group_management_scenario(self):
        """Test typical usage scenario for group management."""
        # Regular user should be able to view groups but not manage them
        request = self.factory.get("/api/groups/")
        request.user = self.regular_user
        self.assertTrue(self.permission.has_permission(request, self.mock_view))

        # Regular user should not be able to create groups
        request = self.factory.post("/api/groups/")
        request.user = self.regular_user
        self.assertFalse(self.permission.has_permission(request, self.mock_view))

        # Admin should be able to create groups
        request = self.factory.post("/api/groups/")
        request.user = self.admin_user
        self.assertTrue(self.permission.has_permission(request, self.mock_view))
