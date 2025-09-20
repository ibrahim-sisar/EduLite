# users/tests/performance/test_mercury_demo.py - Simple demo of Mercury performance framework
"""
Simple demonstration of the Mercury performance testing framework working.

This demonstrates that the EduLite Performance Testing Framework (Mercury) is:
- Successfully initialized
- Monitoring test execution
- Providing performance analysis and scoring
- Detecting threshold violations
- Offering educational guidance
"""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

# Import Mercury performance testing framework
from django_mercury import DjangoMercuryAPITestCase

MERCURY_AVAILABLE = True

from unittest import skipIf


class MercuryFrameworkDemo(DjangoMercuryAPITestCase):
    """
    Simple demonstration that Mercury performance framework is working.

    Shows Mercury's capabilities:
    - Automatic performance monitoring
    - Intelligent threshold management
    - Performance scoring with letter grades
    - Educational guidance for optimization
    """

    @classmethod
    def setUpClass(cls):
        """Configure Mercury framework for demonstration."""
        super().setUpClass()

        if MERCURY_AVAILABLE:
            print("🚀 Initializing Mercury Performance Framework Demo...")
            try:
                cls.configure_mercury(
                    enabled=True,
                    auto_scoring=True,
                    verbose_reporting=True,  # Enable detailed output
                    educational_guidance=True,  # Show optimization tips
                )

                # Set demonstration thresholds
                cls.set_performance_thresholds(
                    {
                        "response_time_ms": 100,  # Quick response expected
                        "query_count_max": 3,  # Minimal queries for simple test
                        "memory_overhead_mb": 20,  # Low memory overhead
                    }
                )
                print("✅ Mercury framework configured successfully!")
            except Exception as e:
                print(f"⚠️ Mercury initialization issue: {e}")
        else:
            print("ℹ️ Mercury framework not available - running basic test")

    def setUp(self):
        """Set up test data."""
        super().setUp()

        self.client = APIClient()

        # Create a simple test user
        self.test_user = User.objects.create_user(
            username="demo_user", email="demo@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.test_user)

    def test_mercury_framework_demonstration(self):
        """
        Demonstrate Mercury framework monitoring a simple API call.

        Mercury will automatically:
        1. Monitor response time, query count, memory usage
        2. Compare against thresholds
        3. Provide performance grade (S, A+, A, B, C, D, F)
        4. Offer optimization suggestions if needed
        """
        print("\n📊 Testing Mercury Performance Monitoring...")

        # Simple API call that Mercury will monitor (using existing endpoint)
        response = self.client.get("/api/users/")

        # Basic functional assertion
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Mercury automatically provides performance analysis
        print(
            "✅ Mercury analysis complete - check output above for performance insights!"
        )

    @skipIf(not MERCURY_AVAILABLE, "Mercury framework not available")
    def test_threshold_violation_educational_demo(self):
        """
        Demonstrate Mercury detecting threshold violations and providing guidance.

        This test intentionally uses very strict thresholds to show Mercury's
        educational guidance when performance expectations aren't met.

        NOTE: This test is EXPECTED to fail with threshold violations -
        that's the point! It demonstrates Mercury's educational features.
        """
        print("\n🎯 Testing Mercury Threshold Detection...")
        print("⚠️  NOTE: This test intentionally sets impossible thresholds")
        print("    to demonstrate Mercury's educational guidance features!")
        print(
            "⚡ EXPECTED RESULT: Test will FAIL to show Mercury's threshold enforcement"
        )

        # Set very strict thresholds to trigger violations
        if MERCURY_AVAILABLE:
            self.set_test_performance_thresholds(
                {
                    "response_time_ms": 1,  # Unrealistically fast
                    "query_count_max": 1,  # Very strict
                    "memory_overhead_mb": 1,  # Very low
                }
            )

        # This will exceed the strict thresholds and FAIL the test
        # That's intentional - it shows Mercury protecting against performance regressions
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Note: Mercury will raise AssertionError before reaching here
        # The educational guidance is shown in the failure output

    def tearDown(self):
        """Clean up after test."""
        super().tearDown()
        print("🧹 Test cleanup complete")

    @classmethod
    def tearDownClass(cls):
        """Final Mercury summary."""
        super().tearDownClass()
        print("\n" + "=" * 60)
        print("🎉 Mercury Performance Framework Demo Complete!")
        print("Key Capabilities Demonstrated:")
        print("  ✅ Automatic performance monitoring")
        print("  ✅ Threshold violation detection")
        print("  ✅ Educational guidance and optimization tips")
        print("  ✅ Performance scoring system")
        print("\nThe framework is ready for comprehensive performance testing!")
        print("=" * 60)


if __name__ == "__main__":
    import unittest

    suite = unittest.TestLoader().loadTestsFromTestCase(MercuryFrameworkDemo)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
