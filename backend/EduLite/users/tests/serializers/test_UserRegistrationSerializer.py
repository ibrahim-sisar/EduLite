from logging import getLogger

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)  # For mocking password validator
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)  # What serializer raises

from django.core import mail
from django.core.signing import TimestampSigner
import base64
import json

logger = getLogger(__name__)

from users.serializers import UserRegistrationSerializer


class UserRegistrationSerializerTests(TestCase):
    def setUp(self):
        """
        Set up common data for tests.
        This password should ideally pass default Django password validators if any are active.
        """
        self.strong_password = "StrongPassword123!"
        self.valid_data_full = {
            "username": "testuser_full",
            "email": "full_user@examplevalid.com",
            "password": self.strong_password,
            "password2": self.strong_password,
            "first_name": "Test",
            "last_name": "UserFull",
        }
        self.valid_data_minimal = {
            "username": "testuser_min",
            "email": "minimal_user@examplevalid.com",
            "password": self.strong_password,
            "password2": self.strong_password,
            # first_name and last_name are optional
        }

    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False
    )
    def test_successful_registration_all_fields(self):
        """Test successful registration with all optional fields provided."""
        serializer = UserRegistrationSerializer(data=self.valid_data_full)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.valid_data_full["username"])
        self.assertEqual(user.email, self.valid_data_full["email"])
        self.assertEqual(user.first_name, self.valid_data_full["first_name"])
        self.assertEqual(user.last_name, self.valid_data_full["last_name"])
        self.assertFalse(user.is_active)  # From serializer's create() method
        self.assertTrue(
            user.check_password(self.valid_data_full["password"])
        )  # Verify password is set and hashed
        
    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=True
    )
    def test_successful_registration_all_fields_email_verification_required(self):
        """Test successful registration with all optional fields provided."""
        serializer = UserRegistrationSerializer(data=self.valid_data_full)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        response = serializer.save()
        self.assertEqual(response['message'], "Verification email sent.")
        
    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False
    )
    def test_successful_registration_minimal_fields(self):
        """Test successful registration with only required fields."""
        serializer = UserRegistrationSerializer(data=self.valid_data_minimal)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.valid_data_minimal["username"])
        self.assertEqual(user.email, self.valid_data_minimal["email"])
        self.assertEqual(user.first_name, "")  # Optional fields should be blank
        self.assertEqual(user.last_name, "")  # Optional fields should be blank
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(self.valid_data_minimal["password"]))
        
    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=True
    )
    def test_successful_registration_minimal_fields_email_verification_required(self):
        """Test successful registration with only required fields."""
        serializer = UserRegistrationSerializer(data=self.valid_data_minimal)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        response = serializer.save()
        self.assertEqual(response['message'], "Verification email sent.")


    def test_missing_required_field_username(self):
        """Test validation error if username is missing."""
        data = self.valid_data_minimal.copy()
        del data["username"]
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertEqual(
            str(serializer.errors["username"][0]), "This field is required."
        )

    def test_missing_required_field_email(self):
        """Test validation error if email is missing."""
        data = self.valid_data_minimal.copy()
        del data["email"]
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(str(serializer.errors["email"][0]), "This field is required.")

    def test_missing_required_field_password(self):
        """Test validation error if password is missing."""
        data = self.valid_data_minimal.copy()
        del data["password"]
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertEqual(
            str(serializer.errors["password"][0]), "This field is required."
        )

    def test_missing_required_field_password2(self):
        """Test validation error if password2 is missing."""
        data = self.valid_data_minimal.copy()
        del data["password2"]
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password2", serializer.errors)
        self.assertEqual(
            str(serializer.errors["password2"][0]), "This field is required."
        )

    def test_password_mismatch(self):
        """Test validation error if password and password2 do not match."""
        data = self.valid_data_minimal.copy()
        data["password2"] = "DifferentPassword123!"
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "password2", serializer.errors
        )  # The error is attached to password2 by your validate method
        self.assertEqual(
            str(serializer.errors["password2"][0]), "Password fields didn't match."
        )

    def test_duplicate_username(self):
        """Test validation error if username already exists."""
        User.objects.create_user(
            username=self.valid_data_minimal["username"], password="somepassword"
        )
        serializer = UserRegistrationSerializer(data=self.valid_data_minimal)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertEqual(
            str(serializer.errors["username"][0]),
            "A user with that username already exists.",
        )

    def test_duplicate_email(self):
        """Test validation error if email already exists."""
        User.objects.create_user(
            username="another_user",
            email=self.valid_data_minimal["email"],
            password="somepassword",
        )
        serializer = UserRegistrationSerializer(data=self.valid_data_minimal)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(
            str(serializer.errors["email"][0]),
            "A user with this email address already exists.",
        )

    @override_settings(BLOCKED_EMAIL_DOMAINS=["example.com"])
    def test_blocked_email_domain(self):
        """Test validation error for an email from a blocked domain."""
        data = self.valid_data_minimal.copy()
        data["email"] = "user@example.com"  # 'example.com' is in your blocked list
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(
            str(serializer.errors["email"][0]),
            "Registration from this email domain is not allowed.",
        )

    def test_email_invalid_format_missing_at_symbol_safeguard(self):
        """Test custom safeguard for email missing '@'."""
        data = self.valid_data_minimal.copy()
        data["email"] = "userexamplevalid.com"
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        # Check if DRF's EmailField caught it or your custom check
        error_messages = [str(err) for err in serializer.errors["email"]]
        self.assertTrue(
            "Enter a valid email address." in error_messages
            or "Invalid email format: '@' symbol missing." in error_messages
        )

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": 10},
            },
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        ]
    )
    def test_weak_password_due_to_length(self):
        """Test password strength validation (too short)."""
        data = self.valid_data_minimal.copy()
        data["password"] = "short"
        data["password2"] = "short"
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        # Example check, the exact message might vary slightly or be a list
        self.assertTrue("too short" in str(serializer.errors["password"][0]).lower())

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        ]
    )
    def test_weak_password_too_common(self):
        """Test password strength validation (too common)."""
        data = self.valid_data_minimal.copy()
        data["password"] = "password"  # A very common password
        data["password2"] = "password"
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertTrue("too common" in str(serializer.errors["password"][0]).lower())

    def test_username_case_insensitivity_check(self):
        """Test that username uniqueness check is case-insensitive."""
        User.objects.create_user(username="TestUser", password="password123")
        data = self.valid_data_minimal.copy()
        data["username"] = "testuser"  # Different case
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertEqual(
            str(serializer.errors["username"][0]),
            "A user with that username already exists.",
        )

    def test_email_case_insensitivity_check(self):
        """Test that email uniqueness check is case-insensitive."""
        User.objects.create_user(
            username="another_user2",
            email="TestEmail@ExampleValid.com",
            password="password123",
        )
        data = self.valid_data_minimal.copy()
        data["email"] = "testemail@examplevalid.com"  # Different case
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(
            str(serializer.errors["email"][0]),
            "A user with this email address already exists.",
        )

    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=True,
        FRONTEND_URL="http://edulite.app"
    )
    def test_verification_email_sent_correctly(self):
        """
        Verify that an email is sent with the correct recipient, subject, and content.
        """
        logger.info("test_verification_email_sent_correctly\n------\n")
        self.assertEqual(len(mail.outbox), 0)
        serializer = UserRegistrationSerializer(data=self.valid_data_full)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]

        logger.info(f"--\tsent_email.body: {sent_email.body}\n")
        
        # Verify email details
        self.assertEqual(sent_email.to, [self.valid_data_full["email"]])
        self.assertIn("Verify your email for EduLite", sent_email.subject)
        
        # Verify both text and HTML content
        self.assertIn(self.valid_data_full["username"], sent_email.body)
        self.assertIn("http://edulite.app/verify-email/?token=", sent_email.body)
        html_body = sent_email.alternatives[0][0]
        self.assertIn(self.valid_data_full["username"], html_body)
        self.assertIn("http://edulite.app/verify-email/?token=", html_body)


    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=False,
        FRONTEND_URL="http://edulite.app"
    )
    def test_verification_email_sent_when_user_is_created(self):
        """
        Verify an email is still sent even when the user is created immediately.
        """
        self.assertEqual(len(mail.outbox), 0)
        serializer = UserRegistrationSerializer(data=self.valid_data_full)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(len(mail.outbox), 1) # Email should be sent
        self.assertEqual(User.objects.count(), 1) # User should be created


    @override_settings(
        USER_EMAIL_VERIFICATION_REQUIRED_FOR_SIGNUP=True,
        FRONTEND_URL="http://edulite.app"
    )
    def test_email_token_payload_is_correct(self):
        """
        Verify that the token in the verification email contains the correct user payload.
        """
        logger.info("test_email_token_payload_is_correct\n------\n")
        self.assertEqual(len(mail.outbox), 0)
        serializer = UserRegistrationSerializer(data=self.valid_data_full)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        sent_email = mail.outbox[0]
        # Extract the token from the link in the email body
        token = sent_email.body.split("?token=")[-1].split('\n')[0].strip()
        logger.info(f"--\ttoken length: {len(token)}\n")

        # Unsign and decode the token to verify its contents
        signer = TimestampSigner()
        try:
            b64_payload = signer.unsign(token, max_age=3600)  # max_age in seconds
            json_payload = base64.urlsafe_b64decode(b64_payload).decode()
            payload = json.loads(json_payload)

            self.assertEqual(payload["email"], self.valid_data_full["email"])
            self.assertEqual(payload["username"], self.valid_data_full["username"])
            self.assertEqual(payload["password"], self.valid_data_full["password"])
            self.assertEqual(payload["first_name"], self.valid_data_full["first_name"])
            self.assertEqual(payload["last_name"], self.valid_data_full["last_name"])

        except Exception as e:
            self.fail(f"Token decoding failed with an exception: {e}")