#!/usr/bin/env python3
"""
RAG Query Cache

WHY: RAG queries are expensive (embedding computation, vector search). Caching
prevents redundant queries for similar code, significantly improving validation
performance for repeated or similar validation requests.

RESPONSIBILITY:
- Cache RAG query results with TTL (time-to-live)
- Implement LRU eviction when cache is full
- Provide O(1) cache lookup and storage
- Manage cache lifecycle and expiration

PATTERNS:
- Cache pattern with TTL
- LRU eviction strategy
- Guard clauses for cache checks
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from rag_validation.rag_example import RAGExample


class RAGQueryCache:
    """
    Caches RAG query results for performance.

    WHY: RAG queries are expensive (embedding computation, vector search).
         Caching prevents redundant queries for similar code.

    WHAT: LRU cache with TTL for RAG query results.
    PERFORMANCE: O(1) lookup, automatic eviction.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache with size and TTL limits.

        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time-to-live for cache entries
        """
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self._cache: Dict[str, Tuple[List[RAGExample], datetime]] = {}

    def get(self, cache_key: str) -> Optional[List[RAGExample]]:
        """
        Retrieve cached RAG results.

        WHY: Avoid expensive RAG queries for repeated validations.
        PERFORMANCE: O(1) dictionary lookup.
        """
        if cache_key not in self._cache:
            return None

        examples, timestamp = self._cache[cache_key]

        # Check if cache entry expired
        if datetime.now() - timestamp > self.ttl:
            del self._cache[cache_key]
            return None

        return examples

    def put(self, cache_key: str, examples: List[RAGExample]) -> None:
        """
        Store RAG results in cache.

        WHY: Cache for future validations of similar code.
        PERFORMANCE: O(1) insertion, O(n) eviction if cache full.
        """
        # Evict oldest entries if cache full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()

        self._cache[cache_key] = (examples, datetime.now())

    def _evict_oldest(self) -> None:
        """
        Evict oldest cache entries.

        WHY: Maintain cache size limit for memory efficiency.
        PERFORMANCE: O(n) to find oldest, could optimize with heap.
        """
        # Guard: empty cache
        if not self._cache:
            return

        # Find oldest entry
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k][1]
        )

        del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
