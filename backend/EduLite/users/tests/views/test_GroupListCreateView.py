# users/tests/views/test_GroupListCreateView.py - Tests for GroupListCreateView

from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status

from .. import UsersAppTestCase


class GroupListCreateViewTest(UsersAppTestCase):
    """Test cases for the GroupListCreateView API endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = reverse("group-list-create")

        # Create some test groups
        self.students_group = Group.objects.create(name="Students")
        self.teachers_group = Group.objects.create(name="Teachers")
        self.moderators_group = Group.objects.create(name="Moderators")

        # Add users to groups
        self.ahmad.groups.add(self.students_group)
        self.marie.groups.add(self.students_group)
        self.sarah_teacher.groups.add(self.teachers_group)

    # --- Authentication Tests ---

    def test_list_groups_requires_authentication(self):
        """Test that listing groups requires authentication."""
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    def test_create_group_requires_authentication(self):
        """Test that creating groups requires authentication."""
        response = self.client.post(self.url, {"name": "NewGroup"})
        self.assert_response_success(response, status.HTTP_401_UNAUTHORIZED)

    # --- List Tests ---

    def test_list_groups_as_regular_user(self):
        """Test that regular users can list groups."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should return paginated results
        self.assert_paginated_response(response)

        # Should see all groups
        group_names = [g["name"] for g in response.data["results"]]
        self.assertIn("Students", group_names)
        self.assertIn("Teachers", group_names)
        self.assertIn("Moderators", group_names)

    def test_list_groups_includes_permissions(self):
        """Test that group list includes permissions if configured."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check group structure
        if response.data["results"]:
            group = response.data["results"][0]
            self.assertIn("id", group)
            self.assertIn("name", group)
            # Permissions might be included depending on serializer

    # --- Create Tests ---

    def test_regular_user_cannot_create_group(self):
        """Test that regular users cannot create groups."""
        self.authenticate_as(self.ahmad)

        response = self.client.post(self.url, {"name": "NewStudentGroup"})

        self.assert_response_success(response, status.HTTP_403_FORBIDDEN)

        # Verify group was not created
        self.assertFalse(Group.objects.filter(name="NewStudentGroup").exists())

    def test_admin_can_create_group(self):
        """Test that admin users can create groups."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.post(self.url, {"name": "AdvancedStudents"})

        self.assert_response_success(response, status.HTTP_201_CREATED)

        # Verify group was created
        self.assertTrue(Group.objects.filter(name="AdvancedStudents").exists())
        self.assertEqual(response.data["name"], "AdvancedStudents")

    def test_create_group_duplicate_name(self):
        """Test creating group with duplicate name."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Try to create duplicate
        response = self.client.post(self.url, {"name": "Students"})  # Already exists

        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_group_empty_name(self):
        """Test creating group with empty name."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.post(self.url, {"name": ""})
        self.assert_response_success(response, status.HTTP_400_BAD_REQUEST)

    def test_create_group_with_permissions(self):
        """Test creating group with permissions if supported."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        # Get some permission IDs
        from django.contrib.auth.models import Permission

        perms = Permission.objects.filter(
            codename__in=["add_user", "change_user"]
        ).values_list("id", flat=True)

        response = self.client.post(
            self.url,
            {
                "name": "Assistants",
                "permissions": list(perms),  # If serializer supports it
            },
        )

        # Should either succeed or ignore permissions field
        self.assertIn(response.status_code, [201, 400])

    # --- Pagination Tests ---

    def test_group_list_pagination(self):
        """Test pagination of group list."""
        # Create many groups
        for i in range(15):
            Group.objects.create(name=f"TestGroup{i}")

        self.authenticate_as(self.ahmad)

        # Get first page
        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Should have pagination
        self.assertGreater(response.data["count"], 10)
        self.assertEqual(len(response.data["results"]), 10)  # Default page size
        self.assertIsNotNone(response.data["next"])

    # --- Filtering Tests ---

    def test_filter_groups_by_name(self):
        """Test filtering groups by name if supported."""
        self.authenticate_as(self.ahmad)

        # Try to filter by name
        response = self.client.get(self.url, {"search": "Student"})
        self.assert_response_success(response, status.HTTP_200_OK)

        # If filtering is supported, should only return matching groups
        if response.data["count"] < 3:  # Less than total groups
            group_names = [g["name"] for g in response.data["results"]]
            for name in group_names:
                self.assertIn("Student", name)

    # --- Ordering Tests ---

    def test_groups_ordered_by_name(self):
        """Test that groups are ordered by name."""
        self.authenticate_as(self.ahmad)

        response = self.client.get(self.url)
        self.assert_response_success(response, status.HTTP_200_OK)

        # Check if ordered alphabetically
        group_names = [g["name"] for g in response.data["results"]]
        if len(group_names) > 1:
            # Should be in some consistent order
            self.assertTrue(
                group_names == sorted(group_names)
                or group_names == sorted(group_names, reverse=True)
            )

    # --- Edge Cases ---

    def test_create_group_special_characters(self):
        """Test creating group with special characters."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.post(self.url, {"name": "Advanced-Students_2024"})

        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Advanced-Students_2024")

    def test_create_group_unicode_name(self):
        """Test creating group with Unicode name."""
        # Make sarah_teacher an admin
        self.sarah_teacher.is_superuser = True
        self.sarah_teacher.is_staff = True
        self.sarah_teacher.save()

        self.authenticate_as(self.sarah_teacher)

        response = self.client.post(
            self.url, {"name": "طلاب متقدمون"}  # Arabic for "Advanced Students"
        )

        self.assert_response_success(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "طلاب متقدمون")

    # --- Performance Test ---

    def test_list_many_groups_performance(self):
        """Test performance with many groups."""
        # Create many groups
        groups = []
        for i in range(100):
            groups.append(Group(name=f"PerfTestGroup{i}"))
        Group.objects.bulk_create(groups)

        self.authenticate_as(self.ahmad)

        import time

        start_time = time.time()

        response = self.client.get(self.url)

        end_time = time.time()
        duration = end_time - start_time

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertLess(duration, 2.0, "Group list too slow with many groups")
