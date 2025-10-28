#!/usr/bin/env python3
"""
WHY: Provide singleton access to global storage manager instance
RESPONSIBILITY: Ensure only one storage manager instance exists per process
PATTERNS: Singleton (global instance), Lazy Initialization

Singleton pattern ensures:
- Single configuration across entire application
- Consistent backend selection
- Resource efficiency (one connection pool, etc.)
"""

from typing import Optional
from output_storage.manager import OutputStorageManager


# Global storage instance
_storage: Optional[OutputStorageManager] = None


def get_storage() -> OutputStorageManager:
    """
    Get or create global storage manager

    Uses lazy initialization - creates instance on first call.

    Returns:
        Global OutputStorageManager instance
    """
    global _storage

    # Guard clause - return existing instance if already created
    if _storage is not None:
        return _storage

    # Lazy initialization - create instance on first call
    _storage = OutputStorageManager()
    return _storage
