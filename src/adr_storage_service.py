#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in adr/storage/.

All functionality has been refactored into:
- adr/storage/rag_storage.py - ADRRagStorage for RAG persistence
- adr/storage/kg_storage.py - ADRKnowledgeGraphStorage for KG operations
- adr/storage/service.py - ADRStorageService (Facade pattern)
- adr/storage/__init__.py - Public API

To migrate your code:
    OLD: from adr_storage_service import ADRStorageService
    NEW: from adr.storage import ADRStorageService

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from adr.storage import ADRStorageService

__all__ = [
    'ADRStorageService',
]
