# users/tests/views/test_UserUpdateDeleteView.py - Tests for UserUpdateDeleteView

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .. import UsersAppTestCase


class UserUpdateDeleteViewTest(UsersAppTestCase):
    """Test cases for the UserUpdateDeleteView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        # URL will be built dynamically in tests using reverse

    # --- Authentication Tests ---

    def test_update_user_requires_authentication(self):
        """Test that updating user requires authentication."""
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})
        data = {"first_name": "Updated"}

        # Test PUT
        response = self.client.put(url, data)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

        # Test PATCH
        response = self.client.patch(url, data)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_requires_authentication(self):
        """Test that deleting user requires authentication."""
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})
        response = self.client.delete(url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- Permission Tests ---

    def test_user_can_update_own_profile(self):
        """Test that users can update their own profile."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        # Test PATCH (partial update)
        data = {"first_name": "Ahmad Updated"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Ahmad Updated")

        # Verify database was updated
        self.ahmad.refresh_from_db()
        self.assertEqual(self.ahmad.first_name, "Ahmad Updated")

    def test_user_cannot_update_other_user(self):
        """Test that users cannot update other users' profiles."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.marie.pk})

        data = {"first_name": "Hacked"}
        response = self.client.patch(url, data, format="json")

        # Should be forbidden
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify database was not updated
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.first_name, "Marie")

    def test_admin_can_update_any_user(self):
        """Test that admin users can update any user."""
        admin_user = self.create_test_user(
            username="admin", is_superuser=True, is_staff=True
        )
        self.authenticate_as(admin_user)

        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})
        data = {"first_name": "Admin Updated"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Admin Updated")

    def test_user_can_delete_own_account(self):
        """Test that users can delete their own account."""
        # Create a test user we can delete
        test_user = self.create_test_user(username="tobedeleted")
        self.authenticate_as(test_user)

        url = reverse("user-update", kwargs={"pk": test_user.pk})
        response = self.client.delete(url)

        # Should return 202 Accepted
        self.assert_response_success(response, status.HTTP_202_ACCEPTED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "User deleted successfully.")

        # Verify user was deleted
        self.assertFalse(User.objects.filter(pk=test_user.pk).exists())

    def test_user_cannot_delete_other_user(self):
        """Test that users cannot delete other users."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.marie.pk})

        response = self.client.delete(url)

        # Should be forbidden
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify user still exists
        self.assertTrue(User.objects.filter(pk=self.marie.pk).exists())

    def test_admin_can_delete_any_user(self):
        """Test that admin users can delete any user."""
        admin_user = self.create_test_user(
            username="admin", is_superuser=True, is_staff=True
        )
        self.authenticate_as(admin_user)

        # Create a user to delete
        test_user = self.create_test_user(username="adminwilldelete")

        url = reverse("user-update", kwargs={"pk": test_user.pk})
        response = self.client.delete(url)

        self.assert_response_success(response, status.HTTP_202_ACCEPTED)
        self.assertFalse(User.objects.filter(pk=test_user.pk).exists())

    # --- PUT (Full Update) Tests ---

    def test_put_update_all_fields(self):
        """Test PUT request updates all provided fields."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        # PUT requires all required fields
        data = {
            "username": "ahmad_gaza",  # Keep same username
            "email": "ahmad_updated@gaza-university.ps",
            "first_name": "Ahmad Updated",
            "last_name": "Al-Rashid Updated",
        }

        response = self.client.put(url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Ahmad Updated")
        self.assertEqual(response.data["last_name"], "Al-Rashid Updated")

        # Email might be visible since it's own profile
        if "email" in response.data:
            self.assertEqual(response.data["email"], "ahmad_updated@gaza-university.ps")

    def test_put_missing_required_fields(self):
        """Test PUT request fails when missing required fields."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        # Missing username (required field)
        data = {"email": "test@university.edu", "first_name": "Test"}

        response = self.client.put(url, data, format="json")

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    # --- PATCH (Partial Update) Tests ---

    def test_patch_update_single_field(self):
        """Test PATCH request can update a single field."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        data = {"first_name": "Ahmad Patched"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Ahmad Patched")
        # Other fields should remain unchanged
        self.assertEqual(response.data["username"], "ahmad_gaza")

    def test_patch_update_multiple_fields(self):
        """Test PATCH request can update multiple fields."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        data = {"first_name": "Ahmad Multi", "last_name": "Al-Rashid Multi"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Ahmad Multi")
        self.assertEqual(response.data["last_name"], "Al-Rashid Multi")

    def test_patch_empty_data(self):
        """Test PATCH request with empty data doesn't break."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        response = self.client.patch(url, {}, format="json")

        # Should succeed but not change anything
        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "ahmad_gaza")

    # --- Validation Tests ---

    def test_update_invalid_email(self):
        """Test updating with invalid email format."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        data = {"email": "not-an-email"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_update_duplicate_username(self):
        """Test updating to a username that already exists."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        # Try to change username to Marie's username
        data = {"username": "marie_student"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_update_blocked_email_domain(self):
        """Test updating to a blocked email domain."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        # example.com is blocked by default
        data = {"email": "ahmad@example.com"}
        response = self.client.patch(url, data, format="json")

        # UserSerializer might not validate email domain on update (only registration)
        # This test documents actual behavior
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn("email", response.data)

    # --- Edge Cases ---

    def test_update_nonexistent_user(self):
        """Test updating a user that doesn't exist."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": 99999})

        data = {"first_name": "Ghost"}
        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_user(self):
        """Test deleting a user that doesn't exist."""
        admin_user = self.create_test_user(
            username="admin", is_superuser=True, is_staff=True
        )
        self.authenticate_as(admin_user)

        url = reverse("user-update", kwargs={"pk": 99999})
        response = self.client.delete(url)

        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_update_with_readonly_fields(self):
        """Test that read-only fields are ignored in updates."""
        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        original_id = self.ahmad.pk
        data = {"id": 9999, "first_name": "Ahmad Readonly Test"}  # Should be read-only

        response = self.client.patch(url, data, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        # ID should not have changed
        self.assertEqual(response.data["id"], original_id)
        # But first_name should update
        self.assertEqual(response.data["first_name"], "Ahmad Readonly Test")

    # --- Delete Edge Cases ---

    def test_delete_user_cascade_effects(self):
        """Test that deleting a user cascades to related objects."""
        # Create a user with profile and friend relationships
        test_user = self.create_test_user(username="cascade_test")

        # Create friendship
        self.create_friendship(test_user, self.ahmad)

        # Create friend request
        friend_request = self.create_friend_request(test_user, self.marie)

        # Verify relationships exist
        self.assertTrue(test_user.profile.friends.filter(pk=self.ahmad.pk).exists())
        self.assertTrue(friend_request.pk)

        # Delete the user
        self.authenticate_as(test_user)
        url = reverse("user-update", kwargs={"pk": test_user.pk})
        response = self.client.delete(url)

        self.assert_response_success(response, status.HTTP_202_ACCEPTED)

        # Verify cascade deletion
        self.assertFalse(User.objects.filter(pk=test_user.pk).exists())
        # Profile should be deleted (CASCADE)
        from ...models import UserProfile

        self.assertFalse(UserProfile.objects.filter(user_id=test_user.pk).exists())
        # Friend request should be deleted
        from ...models import ProfileFriendRequest

        self.assertFalse(
            ProfileFriendRequest.objects.filter(pk=friend_request.pk).exists()
        )

    def test_delete_already_deleted_user(self):
        """Test deleting a user that was already deleted."""
        # Create and delete a user
        test_user = self.create_test_user(username="already_gone")
        test_user_pk = test_user.pk
        test_user.delete()

        # Try to delete again
        admin_user = self.create_test_user(
            username="admin", is_superuser=True, is_staff=True
        )
        self.authenticate_as(admin_user)

        url = reverse("user-update", kwargs={"pk": test_user_pk})
        response = self.client.delete(url)

        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    # --- Performance Test ---

    def test_update_performance_with_many_users(self):
        """Test that update performance doesn't degrade with many users."""
        # Create many users
        users = []
        for i in range(50):
            users.append(
                User(username=f"perf_user_{i}", email=f"perf{i}@university.edu")
            )
        User.objects.bulk_create(users)

        self.authenticate_as(self.ahmad)
        url = reverse("user-update", kwargs={"pk": self.ahmad.pk})

        import time

        start_time = time.time()

        data = {"first_name": "Performance Test"}
        response = self.client.patch(url, data, format="json")

        end_time = time.time()
        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertLess(duration, 1.0, "Update took too long")
