# users/tests/test_views.py (or your chosen test file name)

import sys
from pathlib import Path

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.test import override_settings

# Add performance testing framework to path
performance_path = Path(__file__).parent.parent.parent.parent.parent / "performance_testing" / "python_bindings"
sys.path.insert(0, str(performance_path))

from django_integration_mercury import DjangoMercuryAPITestCase

class UserRegistrationViewTests(DjangoMercuryAPITestCase):
    def setUp(self):
        self.register_url = reverse("user-register")
        self.strong_password = "StrongPassword123!"
        self.user_data = {
            "username": "newtestuser",
            "email": "newtestuser@examplevalid.com",
            "password": self.strong_password,
            "password2": self.strong_password,
            "first_name": "TestFirst",
            "last_name": "TestLast",
        }
        self.minimal_user_data = {
            "username": "minimaluser",
            "email": "minimal@examplevalid.com",
            "password": self.strong_password,
            "password2": self.strong_password,
            # first_name and last_name are optional
        }

    def test_successful_user_registration_all_fields(self):
        """Ensure new user can be registered with all valid fields."""
        self.set_test_performance_thresholds({
            'response_time_ms': 1000,
            'query_count_max': 10,
            'memory_overhead_mb': 20
        })
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(User.objects.count(), 1)
        created_user = User.objects.get(username="newtestuser")
        self.assertEqual(created_user.email, self.user_data["email"])
        self.assertEqual(created_user.first_name, self.user_data["first_name"])
        self.assertEqual(created_user.last_name, self.user_data["last_name"])
        self.assertTrue(
            created_user.is_active
        )  # TODO: Setup email verification, or other means of account activation
        self.assertTrue(
            created_user.check_password(self.strong_password)
        )  # Check password was set and hashed

        # Check response content
        self.assertEqual(response.data["message"], "User created successfully.")
        self.assertEqual(response.data["username"], "newtestuser")
        self.assertEqual(response.data["user_id"], created_user.id)

    def test_successful_user_registration_minimal_fields(self):
        """Ensure new user can be registered with only required fields."""
        self.set_test_performance_thresholds({
            'response_time_ms': 1000,
            'query_count_max': 10,
            'memory_overhead_mb': 20
        })
        response = self.client.post(
            self.register_url, self.minimal_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(User.objects.count(), 1)
        created_user = User.objects.get(username="minimaluser")
        self.assertEqual(created_user.first_name, "")  # Optional field
        self.assertEqual(created_user.last_name, "")  # Optional field
        self.assertTrue(created_user.is_active)

    def test_registration_fails_if_username_missing(self):
        """Ensure registration fails if username is not provided."""
        data = self.user_data.copy()
        del data["username"]
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertEqual(str(response.data["username"][0]), "This field is required.")

    def test_registration_fails_if_passwords_do_not_match(self):
        """Ensure registration fails if password and password2 differ."""
        data = self.user_data.copy()
        data["password2"] = "differentfrompassword1"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)
        self.assertEqual(
            str(response.data["password2"][0]), "Password fields didn't match."
        )

    def test_registration_fails_for_duplicate_username(self):
        """Ensure registration fails if username already exists."""
        User.objects.create_user(
            username=self.user_data["username"], password="somepassword"
        )
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertEqual(
            str(response.data["username"][0]),
            "A user with that username already exists.",
        )

    def test_registration_fails_for_duplicate_email(self):
        """Ensure registration fails if email already exists."""
        User.objects.create_user(
            username="anotheruser",
            email=self.user_data["email"],
            password="somepassword",
        )
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            str(response.data["email"][0]),
            "A user with this email address already exists.",
        )

    def test_registration_fails_for_blocked_email_domain(self):
        """Ensure registration fails for an email from a blocked domain."""
        data = self.user_data.copy()
        data["email"] = (
            "user@example.com"  # 'example.com' is blocked in your serializer
        )
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(
            str(response.data["email"][0]),
            "Registration from this email domain is not allowed.",
        )

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": 20},
            },
        ]
    )
    def test_registration_fails_for_weak_password_too_short(self):
        """Ensure registration fails if password doesn't meet strength requirements (e.g., too short)."""
        data = self.user_data.copy()
        data["password"] = "short"
        data["password2"] = "short"
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        # The exact message depends on the validator
        self.assertTrue("too short" in str(response.data["password"][0]).lower())
