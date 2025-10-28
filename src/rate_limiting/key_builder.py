#!/usr/bin/env python3
"""
WHY: Construct Redis keys for rate limiting
RESPONSIBILITY: Build namespaced keys for resources and identifiers
PATTERNS: Builder (key construction)

Key structure enables per-resource, per-identifier rate limits.
"""


class RateLimitKeyBuilder:
    """
    Builds Redis keys for rate limiting.

    WHY: Centralized key construction ensures consistent namespacing.
    RESPONSIBILITY: Generate keys with proper prefix/resource/identifier structure.
    PATTERNS: Builder pattern.
    """

    def __init__(self, key_prefix: str = "artemis:ratelimit"):
        """
        Initialize key builder.

        Args:
            key_prefix: Redis key prefix for namespacing
        """
        self.key_prefix = key_prefix

    def build_key(self, resource: str, identifier: str) -> str:
        """
        Build Redis key for resource and identifier.

        WHY: Separate rate limits per resource (API endpoint) and identifier (user).

        Args:
            resource: Resource name (e.g., "llm_api", "openai:gpt-4o")
            identifier: User/client identifier

        Returns:
            Formatted Redis key

        Example:
            >>> builder = RateLimitKeyBuilder("artemis:ratelimit")
            >>> builder.build_key("openai:gpt-4o", "user123")
            "artemis:ratelimit:openai:gpt-4o:user123"
        """
        return f"{self.key_prefix}:{resource}:{identifier}"
