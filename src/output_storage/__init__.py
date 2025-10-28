#!/usr/bin/env python3
"""
WHY: Provide unified API for pipeline output storage (local, S3, GCS)
RESPONSIBILITY: Export storage manager and convenience functions
PATTERNS: Strategy (storage backends), Singleton (global instance), Facade

This package provides multi-backend storage for Artemis pipeline outputs:
- Local filesystem storage (default)
- AWS S3 storage
- Google Cloud Storage

Example:
    from output_storage import get_storage

    storage = get_storage()
    path = storage.write_adr(card_id="card-001", adr_number="001", content=adr)
"""

from output_storage.manager import OutputStorageManager
from output_storage.singleton import get_storage

__all__ = ['OutputStorageManager', 'get_storage']
