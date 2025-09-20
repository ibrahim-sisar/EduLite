# users/tests/__init__.py - Base test classes for users app tests

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import json
from pathlib import Path

from ..models import UserProfile, ProfileFriendRequest, UserProfilePrivacySettings


class UsersAppTestCase(APITestCase):
    """
    Base test case for users app tests.

    Uses realistic fixtures representing global user personas from:
    - Students in conflict zones (Gaza, Ukraine)
    - Rural communities (Romania, Nigeria, Peru)
    - Refugee camps (Syria, Somalia)
    - Indigenous communities (Canada, Mexico)
    - Inner cities (France, USA, Brazil)

    Provides:
    - Realistic test data via fixtures
    - Common test utilities
    - Helper methods for user operations
    """

    # Load realistic user personas programmatically (fixtures conflict with signals)
    # fixtures = ['users.json']  # Commented out due to signal conflicts

    @classmethod
    def setUpTestData(cls):
        """Create shared test data once per test class.

        This method is designed by Django specifically for creating test data
        that is shared across all test methods in the class. It runs after
        the test database is created and within a transaction that gets
        rolled back after each test method.
        """
        super().setUpTestData()

        from .fixtures.test_data_generators import (
            create_students_bulk,
            create_teachers_bulk,
            setup_friend_relationships,
        )

        # Create students and teachers in bulk
        cls.students = create_students_bulk()
        cls.teachers = create_teachers_bulk()

        # Set up friend relationships
        setup_friend_relationships(cls.students, cls.teachers)

        # Create easy access attributes
        cls.ahmad = cls.students["ahmad"]  # Gaza, Palestine
        cls.marie = cls.students["marie"]  # Syrian refugee in France
        cls.joy = cls.students["joy"]  # Nigeria, limited data
        cls.elena = cls.students["elena"]  # Rural Romania
        cls.james = cls.students["james"]  # Indigenous Canada
        cls.fatima = cls.students["fatima"]  # Sudan
        cls.miguel = cls.students["miguel"]  # Brazil favela
        cls.sophie = cls.students["sophie"]  # Homeless, Paris
        cls.dmitri = cls.students["dmitri"]  # Ukraine displaced
        cls.maria = cls.students["maria"]  # Mexico indigenous

        # Teachers
        cls.sarah_teacher = cls.teachers["sarah"]  # Toronto, Canada
        cls.dr_ahmed = cls.teachers["ahmed"]  # Cairo, Egypt
        cls.prof_okonkwo = cls.teachers["okonkwo"]  # Rural Nigeria

    def setUp(self):
        """Set up test client."""
        super().setUp()
        self.client = APIClient()
        # Personas are available as class attributes

        # Track created test users for cleanup and reuse
        self._test_users = []

    def authenticate_as(self, user):
        """
        Authenticate the test client as the given user.

        Args:
            user: User instance to authenticate as
        """
        self.client.force_authenticate(user=user)

    def create_test_user(
        self, username="testuser", email=None, password="testpass123", **kwargs
    ):
        """
        Helper to create a test user with profile.

        For better performance, this method will reuse existing test users
        when possible (e.g., for authentication tests).

        Args:
            username: Username for the user
            email: Email (defaults to username@test.com)
            password: Password for the user
            **kwargs: Additional fields for User model

        Returns:
            User instance with profile created via signal
        """
        # For common test usernames, try to reuse existing personas
        reusable_usernames = {
            "test_auth_user": self.ahmad,
            "auth_user": self.marie,
            "admin": self.sarah_teacher,  # Teachers often have admin-like permissions
            "test_user": self.james,
            "auth_user_paginate": self.elena,
            "auth_user_custom_page": self.fatima,
            "auth_user_bulk": self.miguel,
            "auth_user_page": self.dmitri,
            "auth_user_order": self.maria,
            "auth_user_profile": self.joy,
            "auth_user_perf": self.dr_ahmed,
        }

        # If it's a reusable username and no special kwargs, return existing user
        if username in reusable_usernames and not kwargs:
            user = reusable_usernames[username]
            # Update admin status if requested
            if username == "admin":
                user.is_superuser = True
                user.is_staff = True
                user.save()
            return user

        # Otherwise create a new user
        if email is None:
            email = f"{username}@test.com"

        user = User.objects.create_user(
            username=username, email=email, password=password, **kwargs
        )

        # Track for potential cleanup
        self._test_users.append(user)

        # Profile and privacy settings are created automatically via signals
        return user

    def create_friendship(self, user1, user2):
        """
        Create a bidirectional friendship between two users.

        Args:
            user1: First user
            user2: Second user
        """
        user1.profile.friends.add(user2)
        user2.profile.friends.add(user1)

    def create_friend_request(self, sender, receiver, message=""):
        """
        Create a friend request between two users.

        Args:
            sender: User sending the request
            receiver: User receiving the request
            message: Optional message for the request

        Returns:
            ProfileFriendRequest instance
        """
        return ProfileFriendRequest.objects.create(
            sender=sender.profile, receiver=receiver.profile, message=message
        )

    def assert_response_success(self, response, expected_status=status.HTTP_200_OK):
        """
        Assert that response has expected success status.

        Args:
            response: Response object
            expected_status: Expected HTTP status code
        """
        self.assertEqual(
            response.status_code,
            expected_status,
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.data if hasattr(response, 'data') else response.content}",
        )

    def assert_paginated_response(self, response, expected_count=None):
        """
        Assert that response is properly paginated.

        Args:
            response: Response object
            expected_count: Expected total count (optional)
        """
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        if expected_count is not None:
            self.assertEqual(response.data["count"], expected_count)

    def assert_user_in_results(self, response, user):
        """
        Assert that a specific user appears in paginated results.

        Args:
            response: Paginated response
            user: User instance to find
        """
        user_ids = [u["id"] for u in response.data.get("results", [])]
        self.assertIn(
            user.id,
            user_ids,
            f"User {user.username} (id={user.id}) not found in results",
        )

    def assert_user_not_in_results(self, response, user):
        """
        Assert that a specific user does NOT appear in paginated results.

        Args:
            response: Paginated response
            user: User instance that should not be found
        """
        user_ids = [u["id"] for u in response.data.get("results", [])]
        self.assertNotIn(
            user.id,
            user_ids,
            f"User {user.username} (id={user.id}) should not be in results",
        )


class UsersModelTestCase(TestCase):
    """
    Base test case for model tests without Mercury overhead.

    Use this for pure model logic tests where performance monitoring
    is not needed.
    """

    def setUp(self):
        """Set up test data."""
        super().setUp()

    def create_test_user(
        self, username="testuser", email=None, password="testpass123", **kwargs
    ):
        """Helper to create a test user with profile."""
        if email is None:
            email = f"{username}@test.com"

        user = User.objects.create_user(
            username=username, email=email, password=password, **kwargs
        )
        return user
