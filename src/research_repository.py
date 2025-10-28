#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in research/.

All functionality has been refactored into:
- research/storage.py - ExampleStorage for RAG persistence
- research/query.py - ExampleQuery for similarity search
- research/deduplicator.py - ExampleDeduplicator for removing duplicates
- research/ranker.py - ExampleRanker for relevance scoring
- research/repository.py - ExampleRepository (Facade pattern)

To migrate your code:
    OLD: from research_repository import ExampleRepository
    NEW: from research import ExampleRepository

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from research import ExampleRepository

__all__ = [
    'ExampleRepository',
]
