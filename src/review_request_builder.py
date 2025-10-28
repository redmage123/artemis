#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in review_request/.

All functionality has been refactored into:
- review_request/models.py - ImplementationFile value object
- review_request/language_detector.py - Language detection
- review_request/validator.py - Validation logic
- review_request/message_formatter.py - Message formatting
- review_request/file_reader.py - File reading
- review_request/builder.py - ReviewRequestBuilder
- review_request/convenience.py - Convenience functions

To migrate your code:
    OLD: from review_request_builder import ReviewRequestBuilder
    NEW: from review_request import ReviewRequestBuilder

    OLD: from review_request_builder import ImplementationFile
    NEW: from review_request import ImplementationFile

    OLD: from review_request_builder import create_review_request
    NEW: from review_request import create_review_request
"""

# Re-export all public APIs from the modular package
from review_request import (
    ImplementationFile,
    ReviewRequestBuilder,
    read_implementation_files,
    create_review_request
)

__all__ = [
    'ImplementationFile',
    'ReviewRequestBuilder',
    'read_implementation_files',
    'create_review_request'
]
