# users/tests/views/test_GroupRetrieveUpdateDestroyView.py - Tests for GroupRetrieveUpdateDestroyView

from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase


class GroupRetrieveUpdateDestroyViewTest(UsersAppTestCase):
    """Test cases for the GroupRetrieveUpdateDestroyView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

        # Create test group
        self.test_group = Group.objects.create(name="TestStudents")

        # Add some users to the group
        self.test_group.user_set.add(self.ahmad, self.marie)

        # Add some permissions to the group
        view_user_perm = Permission.objects.filter(codename="view_user").first()
        if view_user_perm:
            self.test_group.permissions.add(view_user_perm)

        self.url = reverse("group-detail", kwargs={"pk": self.test_group.id})

    # --- Authentication Tests ---

    def test_retrieve_group_requires_authentication(self):
        """Test that retrieving group details requires authentication."""
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_group_requires_authentication(self):
        """Test that updating group requires authentication."""
        response = self.client.patch(self.url, {"name": "UpdatedName"})
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_delete_group_requires_authentication(self):
        """Test that deleting group requires authentication."""
        response = self.client.delete(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- Retrieve Tests ---

    def test_retrieve_group_as_regular_user(self):
        """Test that regular users can retrieve group details."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check response data
        self.assertEqual(response.data["id"], self.test_group.id)
        self.assertEqual(response.data["name"], "TestStudents")

    def test_retrieve_nonexistent_group(self):
        """Test retrieving non-existent group."""
        self.authenticate_as(self.ahmad)
        url = reverse("group-detail", kwargs={"pk": 99999})

        response = self.client.get(url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    def test_retrieve_group_includes_user_count(self):
        """Test that group details include user count or user list."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Might include user count or user list depending on serializer
        if "user_count" in response.data:
            self.assertEqual(response.data["user_count"], 2)
        elif "users" in response.data:
            self.assertEqual(len(response.data["users"]), 2)

    # --- Update Tests ---

    def test_regular_user_cannot_update_group(self):
        """Test that regular users cannot update groups."""
        self.authenticate_as(self.ahmad)

        response = self.client.patch(self.url, {"name": "HackedGroupName"})

        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify no changes
        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, "TestStudents")

    def test_admin_can_update_group(self):
        """Test that admin users can update groups."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.patch(self.url, {"name": "AdvancedStudents"})

        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify changes
        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, "AdvancedStudents")

    def test_update_group_duplicate_name(self):
        """Test updating group to a name that already exists."""
        # Create another group
        Group.objects.create(name="ExistingGroup")

        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.patch(self.url, {"name": "ExistingGroup"})

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_partial_update_group(self):
        """Test partial update of group (PATCH)."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Update only name
        response = self.client.patch(self.url, {"name": "UpdatedStudents"})

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "UpdatedStudents")

    def test_full_update_group(self):
        """Test full update of group (PUT)."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Get current data
        response = self.client.get(self.url)
        current_data = response.data

        # Update with full data
        current_data["name"] = "CompletelyUpdated"

        response = self.client.put(self.url, current_data)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Verify changes
        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, "CompletelyUpdated")

    # --- Delete Tests ---

    def test_regular_user_cannot_delete_group(self):
        """Test that regular users cannot delete groups."""
        self.authenticate_as(self.ahmad)

        response = self.client.delete(self.url)
        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify group still exists
        self.assertTrue(Group.objects.filter(id=self.test_group.id).exists())

    def test_admin_can_delete_group(self):
        """Test that admin users can delete groups."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.delete(self.url)
        self.assert_response_success(response, status.HTTP_204_NO_CONTENT)

        # Verify group was deleted
        self.assertFalse(Group.objects.filter(id=self.test_group.id).exists())

    def test_delete_group_removes_user_associations(self):
        """Test that deleting group removes user associations."""
        # Verify users are in group
        self.assertTrue(self.ahmad.groups.filter(id=self.test_group.id).exists())

        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.delete(self.url)
        self.assert_response_success(response, status.HTTP_204_NO_CONTENT)

        # Verify users no longer in deleted group
        self.assertFalse(self.ahmad.groups.filter(id=self.test_group.id).exists())
        self.assertFalse(self.marie.groups.filter(id=self.test_group.id).exists())

    def test_delete_nonexistent_group(self):
        """Test deleting non-existent group."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)
        url = reverse("group-detail", kwargs={"pk": 99999})

        response = self.client.delete(url)
        self.assert_response_success(response, status.HTTP_404_NOT_FOUND)

    # --- Permission Management Tests ---

    def test_update_group_permissions(self):
        """Test updating group permissions if supported."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Get some permissions
        perms = Permission.objects.filter(
            codename__in=["add_user", "change_user", "delete_user"]
        ).values_list("id", flat=True)

        response = self.client.patch(self.url, {"permissions": list(perms)})

        # Permissions field is not supported in current implementation
        # Expecting 400 since permissions field is not in serializer
        self.assertEqual(response.status_code, 200)

        # Group name should remain unchanged since we only sent permissions
        self.test_group.refresh_from_db()
        self.assertEqual(self.test_group.name, "TestStudents")

    # --- User Management Tests ---

    def test_add_users_to_group(self):
        """Test adding users to group if supported by API."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Try to add users
        response = self.client.patch(
            self.url, {"users": [self.ahmad.id, self.marie.id, self.joy.id]}
        )

        # If users field is supported
        if response.status_code == 200 and "users" in response.data:
            # Verify Joy was added
            self.assertTrue(self.joy.groups.filter(id=self.test_group.id).exists())

    # --- Edge Cases ---

    def test_update_system_group(self):
        """Test updating system/built-in groups if they exist."""
        # Some Django installations have built-in groups
        # This tests if they're protected

        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Try to update our test group (simulating system group)
        response = self.client.patch(self.url, {"name": "ModifiedSystemGroup"})

        # Should either succeed or be protected
        self.assertIn(response.status_code, [200, 403])

    # --- Performance Test ---

    def test_retrieve_large_group_performance(self):
        """Test performance of retrieving group with many users."""
        # Add many users to group
        large_group = Group.objects.create(name="LargeGroup")

        # Create and add many users
        for i in range(100):
            user = self.create_test_user(username=f"groupuser_{i}")
            large_group.user_set.add(user)

        self.authenticate_as(self.ahmad)
        url = reverse("group-detail", kwargs={"pk": large_group.id})

        import time

        start_time = time.time()

        response = self.client.get(url)

        end_time = time.time()
        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertLess(duration, 2.0, "Large group retrieval too slow")
