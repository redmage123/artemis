#!/usr/bin/env python3
"""
Module: core/exceptions/filesystem.py

WHY: Centralizes all file system and I/O related exceptions. File operations
     are pervasive across Artemis (reading requirements, writing code, saving
     outputs). This module isolates file I/O concerns from business logic.

RESPONSIBILITY: Define file system-specific exception types for file not found,
                read errors, and write errors. Single Responsibility - file I/O only.

PATTERNS: Exception Hierarchy Pattern, I/O Operation Pattern
          - Hierarchy: Base ArtemisFileError with operation-specific subtypes
          - Operations: Read vs Write vs Not Found (different recovery strategies)

Integration: Used by output_storage.py, document_reader.py, all stages that
             write outputs, and any component that performs file I/O.

Design Decision: Why separate file errors from general exceptions?
    File errors have specific recovery strategies (retry, fallback paths,
    permission fixes). Separate module enables I/O-specific error handling.
"""

from core.exceptions.base import ArtemisException


class ArtemisFileError(ArtemisException):
    """
    Base exception for file operations.

    WHY: File operations are common source of errors (permissions, disk space,
         missing files). Enables catching all file errors for I/O recovery.

    RESPONSIBILITY: Base class for file not found, read, and write errors.

    PATTERNS: Exception Hierarchy - specific I/O operations inherit from this

    Use case:
        try:
            file_operation()
        except ArtemisFileError as e:  # Catches all file errors
            use_fallback_storage()
    """
    pass


class FileNotFoundError(ArtemisFileError):
    """
    Required file not found.

    WHY: File not found errors need different handling than permission or
         write errors. May indicate invalid path, deleted file, or config issue.

    PATTERNS: Fail Fast Pattern - missing required files should fail immediately

    Example context:
        {"file_path": "/path/to/requirements.pdf", "operation": "read",
         "checked_paths": ["/path/to/requirements.pdf", "/alt/path/requirements.pdf"]}
    """
    pass


class FileWriteError(ArtemisFileError):
    """
    Error writing file.

    WHY: Write errors indicate disk space, permissions, or file system issues.
         Different recovery than read errors (check space, fix permissions).

    Example context:
        {"file_path": "/path/to/output.py", "operation": "write",
         "error": "PermissionError", "required_space_mb": 100, "available_space_mb": 50}
    """
    pass


class FileReadError(ArtemisFileError):
    """
    Error reading file.

    WHY: Read errors indicate permissions, corruption, or encoding issues.
         Different from file not found - file exists but can't be read.

    Example context:
        {"file_path": "/path/to/input.py", "operation": "read",
         "error": "UnicodeDecodeError", "encoding": "utf-8", "file_size_kb": 500}
    """
    pass
