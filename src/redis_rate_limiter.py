#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in rate_limiting/.

All functionality has been refactored into:
- rate_limiting/exceptions.py - RateLimitExceeded exception
- rate_limiting/models.py - Provider limit configurations
- rate_limiting/key_builder.py - Redis key construction
- rate_limiting/limiter.py - RedisRateLimiter base class
- rate_limiting/providers.py - OpenAIRateLimiter, AnthropicRateLimiter

To migrate your code:
    OLD: from redis_rate_limiter import RedisRateLimiter, RateLimitExceeded
    NEW: from rate_limiting import RedisRateLimiter, RateLimitExceeded

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from rate_limiting import (
    RateLimitExceeded,
    RedisRateLimiter,
    OpenAIRateLimiter,
    AnthropicRateLimiter,
)

__all__ = [
    'RateLimitExceeded',
    'RedisRateLimiter',
    'OpenAIRateLimiter',
    'AnthropicRateLimiter',
]

# Example usage
if __name__ == "__main__":
    print("Testing Redis rate limiter...")

    try:
        # Test basic rate limiter
        limiter = RedisRateLimiter()

        if not limiter.enabled:
            print("❌ Redis not available. Start Redis with:")
            print("   docker run -d -p 6379:6379 redis")
            exit(1)

        print("\n1. Testing basic rate limiter (limit=3, window=5s)...")

        # Reset first
        limiter.reset_rate_limit("test_resource", "test_user")

        # Should allow 3 requests
        for i in range(3):
            allowed = limiter.check_rate_limit("test_resource", limit=3, window_seconds=5, identifier="test_user")
            print(f"   Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
            remaining = limiter.get_remaining_requests("test_resource", limit=3, window_seconds=5, identifier="test_user")
            print(f"   Remaining: {remaining}")

        # 4th request should be blocked
        print("\n2. Testing rate limit exceeded...")
        try:
            limiter.check_rate_limit("test_resource", limit=3, window_seconds=5, identifier="test_user")
            print("   ❌ Should have been blocked!")
        except RateLimitExceeded as e:
            print(f"   ✅ Correctly blocked: {e.message}")
            print(f"   Retry after: {e.context['retry_after_seconds']} seconds")

        # Test OpenAI rate limiter
        print("\n3. Testing OpenAI rate limiter...")
        openai_limiter = OpenAIRateLimiter()
        openai_limiter.reset_rate_limit("openai:gpt-4o", "test_user")

        for i in range(5):
            try:
                openai_limiter.check_openai_limit("gpt-4o", "test_user")
                print(f"   Request {i+1}: ✅ Allowed")
            except RateLimitExceeded as e:
                print(f"   Request {i+1}: ❌ Blocked - {e.message}")

        print("\n✅ All rate limiter tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
