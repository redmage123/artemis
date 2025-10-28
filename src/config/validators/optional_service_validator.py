#!/usr/bin/env python3
"""
Optional Service Validation Module

WHY: Validates optional services if configured (e.g., Redis for caching)

RESPONSIBILITY: Validate availability of optional services when configured

PATTERNS: Guard clauses for early returns, pure validation logic
"""

import os
from typing import List
from ..models import ValidationResult


class OptionalServiceValidator:
    """
    Validates optional services

    WHY: Single Responsibility - handles only optional service validation

    PATTERNS: Guard clauses for early returns
    """

    def validate_optional_services(self) -> List[ValidationResult]:
        """
        Check optional services

        WHY: Validates optional services if configured
        PERFORMANCE: O(1) environment variable check, O(n) for Redis if present

        Returns:
            List of ValidationResult for optional service checks
        """
        results = []
        redis_url = os.getenv("REDIS_URL")

        # Guard clause: No Redis configured
        if not redis_url:
            return results

        results.append(self._check_redis_service(redis_url))
        return results

    def _check_redis_service(self, redis_url: str) -> ValidationResult:
        """
        Check Redis service availability

        WHY: Extracted to avoid nested if statements and improve testability
        PERFORMANCE: Uses socket_connect_timeout to avoid long waits (O(1) with timeout)

        Args:
            redis_url: Redis connection URL

        Returns:
            ValidationResult for Redis check
        """
        try:
            import redis
            client = redis.from_url(redis_url, socket_connect_timeout=2)
            client.ping()
            return ValidationResult(
                check_name="Redis (Optional)",
                passed=True,
                message=f"Connected to Redis at {redis_url}",
                severity="info"
            )
        except ImportError:
            return ValidationResult(
                check_name="Redis (Optional)",
                passed=False,
                message="redis library not installed",
                severity="warning",
                fix_suggestion="pip install redis (optional)"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Redis (Optional)",
                passed=False,
                message=f"Cannot connect to Redis: {e}",
                severity="warning",
                fix_suggestion="Ensure Redis is running or unset REDIS_URL"
            )
