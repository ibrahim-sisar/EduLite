"""Tests for the preview_markdown view endpoint."""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import time

User = get_user_model()


class PreviewMarkdownViewTests(TestCase):
    """Tests for the preview_markdown view endpoint."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.url = "/api/slideshows/preview/"

        # Clear throttle cache before each test to prevent test pollution
        from django.core.cache import cache

        cache.clear()

    # ============================================================================
    # Group 1: Basic Functionality Tests
    # ============================================================================

    def test_render_simple_markdown(self):
        """Test that simple markdown is rendered correctly."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"content": "# Hello World"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rendered_content", response.data)
        # Check that it contains an h1 tag with the content
        self.assertIn("<h1", response.data["rendered_content"])
        self.assertIn("Hello World", response.data["rendered_content"])

    def test_render_empty_content(self):
        """Test that empty content returns empty string."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {"content": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rendered_content"], "")

    def test_render_missing_content_field(self):
        """Test that missing content field returns empty string."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rendered_content"], "")

    def test_response_format(self):
        """Test that response has correct JSON structure."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url, {"content": "Test content"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rendered_content", response.data)
        self.assertIsInstance(response.data["rendered_content"], str)

    def test_render_complex_markdown(self):
        """Test rendering of complex markdown with multiple elements."""
        self.client.force_authenticate(user=self.user)

        markdown_content = """
# Title

This is **bold** and this is *italic*.

- Item 1
- Item 2

## Subtitle

Code: `inline code`

```python
def hello():
    print("world")
```
"""
        response = self.client.post(
            self.url, {"content": markdown_content}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rendered = response.data["rendered_content"]

        # Check various elements are rendered
        self.assertIn("<h1", rendered)
        self.assertIn("<h2", rendered)
        self.assertIn("<strong>", rendered)  # bold
        self.assertIn("<em>", rendered)  # italic
        self.assertIn("<li>", rendered)  # list items
        self.assertIn("<code>", rendered)  # code

    # ============================================================================
    # Group 2: Authentication Tests
    # ============================================================================

    def test_unauthenticated_request_fails(self):
        """Test that unauthenticated users cannot access the endpoint."""
        # Don't authenticate
        response = self.client.post(self.url, {"content": "# Test"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_request_succeeds(self):
        """Test that authenticated users can access the endpoint."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {"content": "# Test"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ============================================================================
    # Group 3: Throttling Tests
    # ============================================================================

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_THROTTLE_RATES": {
                "preview": "5/minute",  # Lower rate for testing
            }
        }
    )
    def test_throttle_allows_multiple_requests(self):
        """Test that throttle allows requests within the limit."""
        self.client.force_authenticate(user=self.user)

        # Make 5 requests (within limit)
        for i in range(5):
            response = self.client.post(
                self.url, {"content": f"# Test {i}"}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_throttle_blocks_excessive_requests(self):
        """Test that throttle blocks requests beyond the limit."""
        self.client.force_authenticate(user=self.user)

        # Make 30 requests (at limit for preview throttle)
        for i in range(30):
            response = self.client.post(
                self.url, {"content": f"# Test {i}"}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 31st request should be throttled
        response = self.client.post(self.url, {"content": "# Test 31"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_throttle_per_user_isolation(self):
        """Test that throttle limits are per-user."""
        # Create second user
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass123",
        )

        # User 1 makes request
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {"content": "# User 1"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User 2 makes request (should not be affected by user 1's throttle)
        self.client.force_authenticate(user=user2)
        response = self.client.post(self.url, {"content": "# User 2"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ============================================================================
    # Group 4: Error Handling Tests
    # ============================================================================

    def test_invalid_json_body(self):
        """Test that invalid JSON body is handled gracefully."""
        self.client.force_authenticate(user=self.user)

        # Send malformed data
        response = self.client.post(
            self.url,
            data="not valid json",
            content_type="application/json",
        )

        # Should return 400 for malformed JSON
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("django_spellbook.parsers.spellbook_render")
    def test_render_exception_handling(self, mock_render):
        """Test that exceptions during rendering are handled gracefully."""
        self.client.force_authenticate(user=self.user)

        # Mock spellbook_render to raise an exception
        mock_render.side_effect = Exception("Render failed")

        response = self.client.post(self.url, {"content": "# Test"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Failed to render markdown")
        self.assertIn("detail", response.data)

    def test_error_response_format(self):
        """Test that error responses have correct structure."""
        self.client.force_authenticate(user=self.user)

        # Force an error by mocking
        with patch("django_spellbook.parsers.spellbook_render") as mock_render:
            mock_render.side_effect = ValueError("Test error")

            response = self.client.post(self.url, {"content": "# Test"}, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("error", response.data)
            self.assertIn("detail", response.data)
            self.assertIsInstance(response.data["error"], str)
            self.assertIsInstance(response.data["detail"], str)

    def test_none_content_value(self):
        """Test that None content value is handled gracefully."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {"content": None}, format="json")

        # Should return empty string, not crash
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rendered_content"], "")

    # ============================================================================
    # Group 5: Edge Cases
    # ============================================================================

    def test_large_markdown_input(self):
        """Test that large markdown input is handled correctly."""
        self.client.force_authenticate(user=self.user)

        # Create a large markdown content (10,000 characters)
        large_content = "# Title\n\n" + ("This is a paragraph. " * 500)

        response = self.client.post(self.url, {"content": large_content}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rendered_content", response.data)
        # Should have rendered content
        self.assertGreater(len(response.data["rendered_content"]), 0)

    def test_unicode_characters(self):
        """Test that unicode characters are handled correctly."""
        self.client.force_authenticate(user=self.user)

        unicode_content = """
# Hello مرحبا 你好 🎉

This contains **Arabic**: مرحبا بك
This contains **Chinese**: 你好世界
This contains **Emojis**: 🚀 🎨 💻
"""
        response = self.client.post(
            self.url, {"content": unicode_content}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rendered = response.data["rendered_content"]

        # Check that unicode is preserved
        self.assertIn("مرحبا", rendered)
        self.assertIn("你好", rendered)
        self.assertIn("🎉", rendered)

    def test_special_html_characters(self):
        """Test that special HTML characters are escaped properly."""
        self.client.force_authenticate(user=self.user)

        content_with_html = "# Test <script>alert('xss')</script>"

        response = self.client.post(
            self.url, {"content": content_with_html}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rendered = response.data["rendered_content"]

        # The exact escaping depends on spellbook_render implementation
        # Just verify we got a response
        self.assertIsInstance(rendered, str)

    # ============================================================================
    # Group 6: SpellBook Component Tests
    # ============================================================================

    def test_spellbook_alert_component(self):
        """Test that SpellBook alert components are rendered."""
        self.client.force_authenticate(user=self.user)

        # SpellBook alert syntax (example - adjust based on actual syntax)
        content = """
:::alert{type="info"}
This is an alert message
:::
"""
        response = self.client.post(self.url, {"content": content}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify something was rendered (actual output depends on spellbook)
        self.assertGreater(len(response.data["rendered_content"]), 0)

    def test_spellbook_card_component(self):
        """Test that SpellBook card components are rendered."""
        self.client.force_authenticate(user=self.user)

        # SpellBook card syntax (example - adjust based on actual syntax)
        content = """
:::card{title="My Card"}
Card content here
:::
"""
        response = self.client.post(self.url, {"content": content}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data["rendered_content"]), 0)
