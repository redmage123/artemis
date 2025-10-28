#!/usr/bin/env python3
"""
Hash-based plan caching using Memento pattern

WHY:
Caching previously generated plans avoids redundant LLM calls and computation,
providing O(1) retrieval for identical tasks. Critical for performance in multi-task pipelines.

RESPONSIBILITY:
- Cache orchestration plans using SHA256 hashes
- Implement LRU eviction for memory management
- Provide O(1) get/put operations

PATTERNS:
- Memento Pattern: Save/restore plan state
- LRU Cache: Least Recently Used eviction policy
- Hash-based Lookup: O(1) average case retrieval

ALGORITHMS:
- Hash Function: SHA256 for cache key generation - O(n) where n=input size
- LRU Eviction: Deque-based tracking - O(1) access/update
- Dictionary Lookup: O(1) average case for get/put
"""

import json
import hashlib
from typing import Dict, Optional, Any
from collections import deque


class PlanCache:
    """
    Hash-based plan caching using Memento pattern

    Industry Algorithm: Hash-based caching for O(1) lookups
    Design Pattern: Memento (save/restore plan state)
    Single Responsibility: Cache and retrieve plans
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize plan cache

        Args:
            max_size: Maximum cache size (LRU eviction)
        """
        self.cache: Dict[str, Any] = {}
        self.access_order: deque = deque()
        self.max_size = max_size

    def _compute_hash(self, card: Dict, platform_hash: str) -> str:
        """
        Compute cache key from card and platform

        Time Complexity: O(n) where n=card content size
        Space Complexity: O(1)

        Args:
            card: Task card
            platform_hash: Platform identifier

        Returns:
            SHA256 hash for cache key
        """
        # Create stable key from task characteristics (O(n))
        key_data = {
            'title': card.get('title', ''),
            'description': card.get('description', ''),
            'priority': card.get('priority', ''),
            'points': card.get('points', 0),
            'platform': platform_hash
        }

        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def get(self, card: Dict, platform_hash: str) -> Optional[Any]:
        """
        Retrieve cached plan with guard clause (early return pattern)

        WHY: Guard clause exits early if key not found, avoiding unnecessary
        LRU bookkeeping operations for cache misses.

        Time Complexity: O(1) average case hash lookup
        """
        cache_key = self._compute_hash(card, platform_hash)

        # Guard clause: Early return for cache miss (O(1))
        if cache_key not in self.cache:
            return None

        # Cache hit: Update LRU order and return (O(1))
        self.access_order.remove(cache_key)
        self.access_order.append(cache_key)
        return self.cache[cache_key]

    def put(self, card: Dict, platform_hash: str, plan: Any) -> None:
        """
        Store plan in cache with LRU eviction

        Time Complexity: O(1) average case
        """
        cache_key = self._compute_hash(card, platform_hash)

        # Evict least recently used if at capacity (O(1))
        if cache_key not in self.cache and len(self.cache) >= self.max_size:
            lru_key = self.access_order.popleft()
            del self.cache[lru_key]

        # Store plan (O(1))
        self.cache[cache_key] = plan
        if cache_key in self.access_order:
            self.access_order.remove(cache_key)
        self.access_order.append(cache_key)
