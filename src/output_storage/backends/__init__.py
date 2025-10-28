#!/usr/bin/env python3
"""
WHY: Provide storage backend implementations for different platforms
RESPONSIBILITY: Export all storage backends (base, local, S3, GCS)
PATTERNS: Strategy (backend selection), ABC (common interface)
"""

from output_storage.backends.base import StorageBackend
from output_storage.backends.local import LocalStorageBackend
from output_storage.backends.s3 import S3StorageBackend
from output_storage.backends.gcs import GCSStorageBackend

__all__ = [
    'StorageBackend',
    'LocalStorageBackend',
    'S3StorageBackend',
    'GCSStorageBackend'
]
