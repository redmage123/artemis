#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in output_storage/.

All functionality has been refactored into:
- output_storage/backends/base.py - StorageBackend ABC
- output_storage/backends/local.py - LocalStorageBackend
- output_storage/backends/s3.py - S3StorageBackend
- output_storage/backends/gcs.py - GCSStorageBackend
- output_storage/factory.py - Backend factory
- output_storage/manager.py - OutputStorageManager
- output_storage/singleton.py - Global instance

To migrate your code:
    OLD: from output_storage import OutputStorageManager, get_storage
    NEW: from output_storage import OutputStorageManager, get_storage  # Same import works!

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from output_storage import OutputStorageManager, get_storage
from output_storage.backends import (
    StorageBackend,
    LocalStorageBackend,
    S3StorageBackend,
    GCSStorageBackend
)

__all__ = [
    'OutputStorageManager',
    'get_storage',
    'StorageBackend',
    'LocalStorageBackend',
    'S3StorageBackend',
    'GCSStorageBackend'
]


# Maintain test script for backward compatibility
if __name__ == "__main__":
    # Test the storage manager
    storage = OutputStorageManager()

    print("Storage Info:")
    print(storage.get_storage_info())

    # Write a test file
    test_path = storage.write_adr("test-card-001", "001", "# Test ADR\n\nThis is a test ADR.")
    print(f"\nWrote test file: {test_path}")

    # Read it back
    content = storage.read_file("adrs/test-card-001/ADR-001.md")
    print(f"\nRead content: {content[:50]}...")

    # List files
    outputs = storage.list_card_outputs("test-card-001")
    print(f"\nCard outputs: {outputs}")
