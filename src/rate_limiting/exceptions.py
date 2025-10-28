#!/usr/bin/env python3
"""
WHY: Define rate limiting exceptions
RESPONSIBILITY: Provide descriptive error for rate limit violations
PATTERNS: Exception hierarchy

Rate limit exception includes retry-after timing information.
"""

from artemis_exceptions import ArtemisException


class RateLimitExceeded(ArtemisException):
    """
    Rate limit exceeded exception.

    WHY: Distinct exception type allows targeted handling of rate limit errors.
    RESPONSIBILITY: Carry rate limit context (retry timing, current usage).
    """
    pass
