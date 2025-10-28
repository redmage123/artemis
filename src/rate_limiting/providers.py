#!/usr/bin/env python3
"""
WHY: Provider-specific rate limiters with preset limits
RESPONSIBILITY: Implement OpenAI and Anthropic rate limiting
PATTERNS: Template Method (base class override), Strategy (provider limits)

Provider limiters use official API limits (conservative defaults).
"""

from typing import Optional

from redis_client import RedisClient
from rate_limiting.limiter import RedisRateLimiter
from rate_limiting.models import OPENAI_LIMITS, ANTHROPIC_LIMITS


class OpenAIRateLimiter(RedisRateLimiter):
    """
    OpenAI-specific rate limiter with preset limits.

    WHY: OpenAI has model-specific rate limits that need enforcement.
    RESPONSIBILITY: Apply conservative OpenAI limits by model.
    PATTERNS: Template Method (inherits from RedisRateLimiter).

    OpenAI limits (as of 2025):
    - GPT-4o: 10,000 requests/min, 2M tokens/min
    - GPT-4o-mini: 30,000 requests/min, 10M tokens/min

    Note: Using conservative defaults (1% of official limits).
    """

    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        Initialize OpenAI rate limiter.

        Args:
            redis_client: Redis client (uses default if not provided)
        """
        super().__init__(redis_client, key_prefix="artemis:ratelimit:openai")
        self.limits = OPENAI_LIMITS

    def check_openai_limit(
        self,
        model: str = "gpt-4o",
        identifier: str = "default"
    ) -> bool:
        """
        Check OpenAI rate limit for specific model.

        WHY: Delegates to base class with model-specific limits.

        Args:
            model: OpenAI model name
            identifier: User/client identifier

        Returns:
            True if request allowed

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        # Dispatch table lookup for limits (no if/elif)
        limits = self.limits.get(model, self.limits["default"])

        return self.check_rate_limit(
            resource=f"openai:{model}",
            limit=limits["requests_per_minute"],
            window_seconds=60,
            identifier=identifier
        )


class AnthropicRateLimiter(RedisRateLimiter):
    """
    Anthropic-specific rate limiter with preset limits.

    WHY: Anthropic has model-specific rate limits that need enforcement.
    RESPONSIBILITY: Apply conservative Anthropic limits by model.
    PATTERNS: Template Method (inherits from RedisRateLimiter).

    Anthropic limits (as of 2025):
    - Claude Sonnet: 5,000 requests/min, 1M tokens/min

    Note: Using conservative defaults (1% of official limits).
    """

    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        Initialize Anthropic rate limiter.

        Args:
            redis_client: Redis client (uses default if not provided)
        """
        super().__init__(redis_client, key_prefix="artemis:ratelimit:anthropic")
        self.limits = ANTHROPIC_LIMITS

    def check_anthropic_limit(
        self,
        model: str = "claude-sonnet-4-5",
        identifier: str = "default"
    ) -> bool:
        """
        Check Anthropic rate limit for specific model.

        WHY: Delegates to base class with model-specific limits.

        Args:
            model: Anthropic model name
            identifier: User/client identifier

        Returns:
            True if request allowed

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        # Dispatch table lookup for limits (no if/elif)
        limits = self.limits.get(model, self.limits["default"])

        return self.check_rate_limit(
            resource=f"anthropic:{model}",
            limit=limits["requests_per_minute"],
            window_seconds=60,
            identifier=identifier
        )
