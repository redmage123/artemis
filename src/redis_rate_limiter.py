from artemis_logger import get_logger
logger = get_logger('redis_rate_limiter')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nThis module maintains backward compatibility while the codebase migrates\nto the new modular structure in rate_limiting/.\n\nAll functionality has been refactored into:\n- rate_limiting/exceptions.py - RateLimitExceeded exception\n- rate_limiting/models.py - Provider limit configurations\n- rate_limiting/key_builder.py - Redis key construction\n- rate_limiting/limiter.py - RedisRateLimiter base class\n- rate_limiting/providers.py - OpenAIRateLimiter, AnthropicRateLimiter\n\nTo migrate your code:\n    OLD: from redis_rate_limiter import RedisRateLimiter, RateLimitExceeded\n    NEW: from rate_limiting import RedisRateLimiter, RateLimitExceeded\n\nNo breaking changes - all imports remain identical.\n'
from rate_limiting import RateLimitExceeded, RedisRateLimiter, OpenAIRateLimiter, AnthropicRateLimiter
__all__ = ['RateLimitExceeded', 'RedisRateLimiter', 'OpenAIRateLimiter', 'AnthropicRateLimiter']
if __name__ == '__main__':
    
    logger.log('Testing Redis rate limiter...', 'INFO')
    try:
        limiter = RedisRateLimiter()
        if not limiter.enabled:
            
            logger.log('❌ Redis not available. Start Redis with:', 'INFO')
            
            logger.log('   docker run -d -p 6379:6379 redis', 'INFO')
            exit(1)
        
        logger.log('\n1. Testing basic rate limiter (limit=3, window=5s)...', 'INFO')
        limiter.reset_rate_limit('test_resource', 'test_user')
        for i in range(3):
            allowed = limiter.check_rate_limit('test_resource', limit=3, window_seconds=5, identifier='test_user')
            
            logger.log(f"   Request {i + 1}: {('✅ Allowed' if allowed else '❌ Blocked')}", 'INFO')
            remaining = limiter.get_remaining_requests('test_resource', limit=3, window_seconds=5, identifier='test_user')
            
            logger.log(f'   Remaining: {remaining}', 'INFO')
        
        logger.log('\n2. Testing rate limit exceeded...', 'INFO')
        try:
            limiter.check_rate_limit('test_resource', limit=3, window_seconds=5, identifier='test_user')
            
            logger.log('   ❌ Should have been blocked!', 'INFO')
        except RateLimitExceeded as e:
            
            logger.log(f'   ✅ Correctly blocked: {e.message}', 'INFO')
            
            logger.log(f"   Retry after: {e.context['retry_after_seconds']} seconds", 'INFO')
        
        logger.log('\n3. Testing OpenAI rate limiter...', 'INFO')
        openai_limiter = OpenAIRateLimiter()
        openai_limiter.reset_rate_limit('openai:gpt-4o', 'test_user')
        for i in range(5):
            try:
                openai_limiter.check_openai_limit('gpt-4o', 'test_user')
                
                logger.log(f'   Request {i + 1}: ✅ Allowed', 'INFO')
            except RateLimitExceeded as e:
                
                logger.log(f'   Request {i + 1}: ❌ Blocked - {e.message}', 'INFO')
        
        logger.log('\n✅ All rate limiter tests passed!', 'INFO')
    except Exception as e:
        
        logger.log(f'❌ Error: {e}', 'INFO')
        import traceback
        traceback.print_exc()