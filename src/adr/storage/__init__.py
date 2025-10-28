#!/usr/bin/env python3
"""
WHY: Public API for ADR storage operations
RESPONSIBILITY: Export ADRStorageService
PATTERNS: Facade (clean public interface)

Storage package provides unified ADR persistence across RAG and KG.
"""

from adr.storage.service import ADRStorageService

__all__ = [
    'ADRStorageService',
]
