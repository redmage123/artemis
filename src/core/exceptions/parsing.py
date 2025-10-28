#!/usr/bin/env python3
"""
Module: core/exceptions/parsing.py

WHY: Centralizes all document and requirements parsing exceptions. Parsing is
     critical for extracting requirements from PDFs, Word docs, and markdown.
     This module isolates parsing concerns from business logic.

RESPONSIBILITY: Define parsing-specific exception types for requirements files,
                document formats, and validation. Single Responsibility - parsing only.

PATTERNS: Exception Hierarchy Pattern, Format Classification Pattern
          - Hierarchy: Base RequirementsException with specific subtypes
          - Classification: By operation (file, parse, validate, export)

Integration: Used by requirements_parser_agent.py, document_reader.py, and
             any component that processes user-provided requirements documents.

Design Decision: Why separate parsing from other file operations?
    Requirements parsing has unique challenges (format detection, content
    extraction, validation). Separate module enables parser-specific strategies.
"""

from core.exceptions.base import ArtemisException


class RequirementsException(ArtemisException):
    """
    Base exception for requirements parsing errors.

    WHY: Requirements parsing is critical first step in pipeline. Enables
         catching all parsing errors and provides clear error categorization.

    RESPONSIBILITY: Base class for requirements file, parsing, validation errors.

    Use case:
        try:
            parse_requirements(file)
        except RequirementsException as e:  # Catches all parsing errors
            request_requirements_fix()
    """
    pass


class RequirementsFileError(RequirementsException):
    """
    Error reading requirements file.

    WHY: File errors (missing, unreadable, wrong permissions) must be
         distinguished from parsing errors. Different recovery strategies.

    Example context:
        {"file_path": "/path/to/requirements.pdf", "error": "FileNotFoundError",
         "expected_formats": ["pdf", "docx", "md"]}
    """
    pass


class RequirementsParsingError(RequirementsException):
    """
    Error parsing requirements content.

    WHY: Parsing errors indicate document structure issues or corrupted content.
         Different from file access errors. May need format-specific parser.

    Example context:
        {"file_path": "/path/to/requirements.pdf", "format": "pdf",
         "parser": "pypdf", "page": 5, "error": "InvalidPDFStructure"}
    """
    pass


class RequirementsValidationError(RequirementsException):
    """
    Requirements validation failed.

    WHY: Validation errors indicate parsed content doesn't meet expected
         structure (missing sections, invalid format). Different from parsing.

    Example context:
        {"required_sections": ["functional", "non-functional"],
         "missing_sections": ["non-functional"], "total_requirements": 10}
    """
    pass


class RequirementsExportError(RequirementsException):
    """
    Error exporting requirements to YAML/JSON.

    WHY: Export errors indicate serialization issues or invalid data structures.
         Different from parsing (input) - this is output error.

    Example context:
        {"export_format": "yaml", "output_path": "/path/to/output.yaml",
         "error": "YAMLSerializationError", "requirement_count": 25}
    """
    pass


class UnsupportedDocumentFormatError(RequirementsException):
    """
    Document format not supported.

    WHY: Format errors should fail fast with clear message about supported
         formats. Prevents wasted parsing attempts on unsupported files.

    PATTERNS: Fail Fast Pattern - no retry, immediate user feedback

    Example context:
        {"file_path": "/path/to/requirements.xyz", "format": "xyz",
         "supported_formats": ["pdf", "docx", "md", "txt"]}
    """
    pass


class DocumentReadError(RequirementsException):
    """
    Error reading document content.

    WHY: Read errors indicate document corruption, encoding issues, or
         format-specific problems. More specific than general file error.

    Example context:
        {"file_path": "/path/to/requirements.docx", "format": "docx",
         "error": "CorruptedZipFile", "file_size_kb": 500}
    """
    pass
