"""
Redis-specific code examples for RAG/KG population.

WHY:
Redis examples showcase advanced data structures, pipelining, Lua scripts,
and patterns for caching, rate limiting, and real-time analytics.

RESPONSIBILITY:
- Provide Redis data structure usage patterns
- Demonstrate atomic operations using Lua scripts
- Show pipelining for network optimization
- Include rate limiting and caching strategies

PATTERNS:
- Use appropriate data structures (strings, hashes, lists, sets, sorted sets)
- Leverage Lua scripts for atomic multi-command operations
- Use pipelining to reduce network round-trips
- Include HyperLogLog for cardinality estimation
- Show Redis Streams for event sourcing
"""

from code_example_types import CodeExample


REDIS_EXAMPLES = [
    CodeExample(
        language="Redis",
        pattern="Redis Data Structures",
        title="Advanced Redis Patterns for Caching and Rate Limiting",
        description="Using Redis data structures efficiently: pipelining, Lua scripts, and HyperLogLog",
        code='''# Redis Advanced Patterns
# Why: Sub-millisecond performance, atomic operations
# Prevents: Race conditions, cache stampede, network round-trips

# ==== STRING OPERATIONS ====

# Simple key-value with expiration (cache pattern)
SET user:1000:profile '{"name":"Alice","email":"alice@example.com"}' EX 3600
GET user:1000:profile

# Atomic increment (counters)
INCR page:views:home
INCRBY page:views:home 10
DECR inventory:product:123

# Atomic operations (prevent race conditions)
SET lock:user:1000 "processing" NX EX 30  # Only set if not exists
GET lock:user:1000
DEL lock:user:1000


# ==== HASH OPERATIONS (for objects) ====

# Store user object as hash (more efficient than JSON string for partial updates)
HSET user:1000 name "Alice" email "alice@example.com" age 30
HGET user:1000 name
HGETALL user:1000
HMGET user:1000 name email  # Get multiple fields

# Atomic increment on hash field
HINCRBY user:1000 login_count 1


# ==== LIST OPERATIONS (for queues, feeds) ====

# Job queue (FIFO)
LPUSH jobs:queue '{"task":"send_email","to":"user@example.com"}'
RPOP jobs:queue  # Blocking: BRPOP jobs:queue 30

# Activity feed (limited size)
LPUSH feed:user:1000 "Alice posted a photo"
LTRIM feed:user:1000 0 99  # Keep only 100 most recent items
LRANGE feed:user:1000 0 19  # Get first 20 items


# ==== SET OPERATIONS (for unique items, relationships) ====

# User's followers
SADD followers:user:1000 2000 3000 4000
SISMEMBER followers:user:1000 2000  # Check membership (O(1))
SCARD followers:user:1000  # Count followers

# Common followers (set intersection)
SINTER followers:user:1000 followers:user:2000

# Suggested friends (followers of followers, excluding existing)
SDIFF followers:user:2000 followers:user:1000


# ==== SORTED SET OPERATIONS (for leaderboards, rankings) ====

# Leaderboard
ZADD leaderboard 1000 "player1" 1500 "player2" 2000 "player3"
ZINCRBY leaderboard 100 "player1"  # Atomic score increment

# Top 10 players
ZREVRANGE leaderboard 0 9 WITHSCORES

# Player rank
ZREVRANK leaderboard "player1"

# Players in score range
ZRANGEBYSCORE leaderboard 1000 2000 WITHSCORES

# Time-based expiration (cleanup old entries)
ZREMRANGEBYSCORE sessions:active 0 1704067200  # Remove before timestamp


# ==== PIPELINING (reduce network round-trips) ====

# Without pipelining: 5 network round-trips
# With pipelining: 1 network round-trip
MULTI
GET user:1000:profile
HGETALL user:1000:stats
ZRANGE leaderboard:daily 0 9
SMEMBERS followers:user:1000
LRANGE feed:user:1000 0 19
EXEC


# ==== LUA SCRIPTS (atomic operations) ====

# Rate limiting using Lua (atomic, prevents race conditions)
EVAL "
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = redis.call('INCR', key)
if current == 1 then
    redis.call('EXPIRE', key, window)
end
if current > limit then
    return 0  -- Rate limit exceeded
else
    return 1  -- Allow request
end
" 1 rate_limit:user:1000:api 100 3600
# Limit: 100 requests per 3600 seconds (1 hour)


# ==== HYPERLOGLOG (cardinality estimation) ====

# Count unique visitors (memory-efficient: ~12KB for billions of items)
PFADD unique:visitors:2025-01-15 "user1" "user2" "user3"
PFCOUNT unique:visitors:2025-01-15  # Approximate count (0.81% error)

# Merge multiple HyperLogLogs
PFMERGE unique:visitors:2025-01-week unique:visitors:2025-01-15 unique:visitors:2025-01-16


# ==== STREAMS (message queue, event sourcing) ====

# Add event to stream
XADD events:user:1000 * action "login" timestamp 1704067200 ip "192.168.1.1"

# Read stream events
XREAD COUNT 10 STREAMS events:user:1000 0

# Consumer groups (competing consumers pattern)
XGROUP CREATE events:user:1000 processors $ MKSTREAM
XREADGROUP GROUP processors consumer1 COUNT 10 STREAMS events:user:1000 >


# ==== CACHE PATTERNS ====

# Cache-aside pattern (lazy loading)
# 1. Try to get from cache
GET product:123
# 2. If cache miss, fetch from database
# 3. Set in cache with expiration
SET product:123 '{"name":"Product","price":99.99}' EX 3600

# Cache stampede prevention (use SETNX for locking)
SET lock:product:123 1 NX EX 10
# If lock acquired, fetch from database and cache
# If lock not acquired, wait and retry


# ==== MONITORING ====

# Get statistics
INFO stats
INFO memory
SLOWLOG GET 10  # Get 10 slowest queries
MONITOR  # Real-time command monitoring (DEV ONLY - impacts performance)
''',
        quality_score=95,
        tags=["Redis", "caching", "data-structures", "pipelining", "lua", "rate-limiting"],
        complexity="advanced",
        demonstrates=["Redis Data Structures", "Pipelining", "Lua Scripts", "HyperLogLog", "Streams", "Rate Limiting"],
        prevents=["Race Conditions", "Cache Stampede", "Network Round-Trips", "Memory Inefficiency"]
    ),
]
