#!/usr/bin/env python3
"""
WHY: Implement sliding window rate limiting with Redis
RESPONSIBILITY: Core rate limit checking and tracking
PATTERNS: Strategy (sliding window algorithm), Composition (Redis client)

Sliding window provides accurate, distributed rate limiting.
"""

import time
from typing import Optional

from redis_client import RedisClient, get_redis_client
from rate_limiting.exceptions import RateLimitExceeded
from rate_limiting.key_builder import RateLimitKeyBuilder


class RedisRateLimiter:
    """
    Token bucket rate limiter using Redis.

    WHY: Prevents hitting LLM API rate limits with distributed tracking.
    RESPONSIBILITY: Check limits, track usage, enforce sliding window.
    PATTERNS: Strategy (sliding window), Composition (Redis client, key builder).

    Features:
    - Sliding window rate limiting
    - Per-user/per-resource limits
    - Distributed rate limiting across multiple instances
    """

    def __init__(
        self,
        redis_client: Optional[RedisClient] = None,
        key_prefix: str = "artemis:ratelimit"
    ):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client (uses default if not provided)
            key_prefix: Redis key prefix for namespacing
        """
        # Guard clause - use provided client or get default
        if redis_client:
            self.redis = redis_client
        else:
            self.redis = get_redis_client(raise_on_error=False)

        self.key_builder = RateLimitKeyBuilder(key_prefix)
        self.enabled = self.redis is not None

        # Guard clause - warn if disabled
        if not self.enabled:
            print("⚠️  Redis not available - Rate limiting disabled")

    def check_rate_limit(
        self,
        resource: str,
        limit: int,
        window_seconds: int,
        identifier: str = "default"
    ) -> bool:
        """
        Check if rate limit allows request.

        WHY: Sliding window algorithm provides accurate rate limiting.

        Args:
            resource: Resource name (e.g., "llm_api", "openai")
            limit: Max requests per window
            window_seconds: Time window in seconds
            identifier: User/client identifier

        Returns:
            True if request allowed

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        # Guard clause - disabled always allows
        if not self.enabled:
            return True

        try:
            key = self.key_builder.build_key(resource, identifier)
            current_time = time.time()
            window_start = current_time - window_seconds

            # Remove old entries outside the window
            self.redis.client.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            request_count = self.redis.client.zcard(key)

            # Guard clause - limit exceeded
            if request_count >= limit:
                retry_after = self._calculate_retry_after(
                    key,
                    window_seconds,
                    current_time
                )

                raise RateLimitExceeded(
                    f"Rate limit exceeded for {resource}",
                    context={
                        "resource": resource,
                        "limit": limit,
                        "window_seconds": window_seconds,
                        "current_count": request_count,
                        "retry_after_seconds": round(retry_after, 2)
                    }
                )

            # Add current request
            self.redis.client.zadd(key, {str(current_time): current_time})

            # Set expiration on the key
            self.redis.expire(key, window_seconds + 60)

            return True

        except RateLimitExceeded:
            raise
        except Exception as e:
            # Don't fail on rate limiter errors - allow request
            print(f"⚠️  Rate limiter error: {e}")
            return True

    def get_remaining_requests(
        self,
        resource: str,
        limit: int,
        window_seconds: int,
        identifier: str = "default"
    ) -> int:
        """
        Get remaining requests in current window.

        WHY: Allows clients to implement adaptive behavior.

        Args:
            resource: Resource name
            limit: Max requests per window
            window_seconds: Time window in seconds
            identifier: User/client identifier

        Returns:
            Number of remaining requests
        """
        # Guard clause - disabled returns full limit
        if not self.enabled:
            return limit

        try:
            key = self.key_builder.build_key(resource, identifier)
            current_time = time.time()
            window_start = current_time - window_seconds

            # Remove old entries
            self.redis.client.zremrangebyscore(key, 0, window_start)

            # Count current requests
            request_count = self.redis.client.zcard(key)

            return max(0, limit - request_count)

        except Exception as e:
            print(f"⚠️  Error getting remaining requests: {e}")
            return limit

    def reset_rate_limit(self, resource: str, identifier: str = "default") -> bool:
        """
        Reset rate limit for a resource.

        WHY: Enables testing and manual limit resets.

        Args:
            resource: Resource name
            identifier: User/client identifier

        Returns:
            True if reset successfully
        """
        # Guard clause - disabled can't reset
        if not self.enabled:
            return False

        try:
            key = self.key_builder.build_key(resource, identifier)
            self.redis.delete(key)
            return True

        except Exception as e:
            print(f"⚠️  Error resetting rate limit: {e}")
            return False

    def _calculate_retry_after(
        self,
        key: str,
        window_seconds: int,
        current_time: float
    ) -> float:
        """
        Calculate retry-after time based on oldest request.

        WHY: Tells client exactly when they can retry.

        Args:
            key: Redis key
            window_seconds: Window size in seconds
            current_time: Current timestamp

        Returns:
            Seconds until retry allowed
        """
        # Get oldest request timestamp
        oldest = self.redis.client.zrange(key, 0, 0, withscores=True)

        # Guard clause - no oldest entry
        if not oldest:
            return window_seconds

        return window_seconds - (current_time - oldest[0][1])
