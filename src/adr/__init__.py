#!/usr/bin/env python3
"""
WHY: Public API for ADR (Architecture Decision Records) package
RESPONSIBILITY: Export ADRStorageService
PATTERNS: Facade (clean public interface)

ADR package provides storage and management of Architecture Decision Records.
"""

from adr.storage import ADRStorageService

__all__ = [
    'ADRStorageService',
]
