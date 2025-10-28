#!/usr/bin/env python3
"""
Module: test_advanced_features/test_retry_policy.py

WHY: Validates retry decision logic and exponential backoff calculations to ensure
     transient failures retry appropriately without infinite loops.

RESPONSIBILITY:
- Test retry within limit
- Test retry exhaustion
- Test exponential backoff calculation

PATTERNS:
- Boundary value testing (at limits, below limits, above limits)
- Guard clauses for validation
"""

import unittest
from dynamic_pipeline import RetryPolicy


class TestRetryPolicy(unittest.TestCase):
    """
    Test retry policy behavior.

    WHAT: Validates retry decision logic and backoff calculations
    WHY: Transient failures should retry with backoff, permanent failures should not
    """

    def test_should_retry_within_limit(self):
        """
        WHAT: Tests retry allowed when within max retry limit
        WHY: Transient failures should be retried to handle temporary issues
        """
        policy = RetryPolicy(max_retries=3)
        exception = Exception("Transient error")

        # Should retry on attempts 0, 1, 2 (within limit)
        self.assertTrue(policy.should_retry(exception, 0))
        self.assertTrue(policy.should_retry(exception, 1))
        self.assertTrue(policy.should_retry(exception, 2))

    def test_should_not_retry_exceeded_limit(self):
        """
        WHAT: Tests retry denied when max retries exceeded
        WHY: Permanent failures should not retry infinitely - fail after limit reached
        """
        policy = RetryPolicy(max_retries=3)
        exception = Exception("Persistent error")

        # Should not retry on attempt 3 (exceeds limit)
        self.assertFalse(policy.should_retry(exception, 3))
        self.assertFalse(policy.should_retry(exception, 4))

    def test_exponential_backoff(self):
        """
        WHAT: Tests backoff delay increases exponentially with attempt count
        WHY: Exponential backoff prevents thundering herd and gives systems time to recover
        """
        policy = RetryPolicy(initial_delay=1.0, backoff_multiplier=2.0)

        # Verify exponential backoff: 1, 2, 4, 8...
        self.assertEqual(policy.get_delay(0), 1.0)
        self.assertEqual(policy.get_delay(1), 2.0)
        self.assertEqual(policy.get_delay(2), 4.0)
        self.assertEqual(policy.get_delay(3), 8.0)
