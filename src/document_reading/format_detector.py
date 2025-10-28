#!/usr/bin/env python3
"""
WHY: Auto-detect document formats from file extensions.
RESPONSIBILITY: Map file extensions to document types using dispatch table pattern.
PATTERNS: Dictionary dispatch for O(1) lookups, Strategy pattern for format detection.
"""

from pathlib import Path
from typing import Dict, Optional
from document_reading.models import DocumentType


class FormatDetector:
    """
    WHY: Centralize document format detection logic.
    RESPONSIBILITY: Determine document type from file path or extension.
    """

    # Dispatch table for O(1) extension lookup
    EXTENSION_MAP: Dict[str, DocumentType] = {
        '.pdf': DocumentType.PDF,
        '.docx': DocumentType.WORD,
        '.doc': DocumentType.WORD,
        '.xlsx': DocumentType.EXCEL,
        '.xls': DocumentType.EXCEL,
        '.odt': DocumentType.ODT,
        '.ods': DocumentType.ODS,
        '.txt': DocumentType.TEXT,
        '.md': DocumentType.MARKDOWN,
        '.markdown': DocumentType.MARKDOWN,
        '.csv': DocumentType.CSV,
        '.html': DocumentType.HTML,
        '.htm': DocumentType.HTML,
        '.ipynb': DocumentType.JUPYTER
    }

    @classmethod
    def detect_from_path(cls, file_path: str) -> DocumentType:
        """
        WHY: Detect document type from file path.
        RESPONSIBILITY: Extract extension and map to DocumentType.

        Args:
            file_path: Path to document file

        Returns:
            Detected DocumentType (UNKNOWN if not recognized)
        """
        extension = Path(file_path).suffix.lower()
        return cls.EXTENSION_MAP.get(extension, DocumentType.UNKNOWN)

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        WHY: Quick check if file format is supported.
        RESPONSIBILITY: Validate file extension is in supported list.

        Args:
            file_path: Path to check

        Returns:
            True if format is supported
        """
        return cls.detect_from_path(file_path) != DocumentType.UNKNOWN

    @classmethod
    def get_extension(cls, file_path: str) -> str:
        """
        WHY: Extract normalized file extension.
        RESPONSIBILITY: Return lowercase extension for consistent handling.

        Args:
            file_path: Path to file

        Returns:
            Lowercase file extension (e.g., '.pdf')
        """
        return Path(file_path).suffix.lower()

    @classmethod
    def get_supported_extensions(cls) -> Dict[DocumentType, list]:
        """
        WHY: Provide list of all supported extensions by type.
        RESPONSIBILITY: Group extensions by document type for reporting.

        Returns:
            Dictionary mapping DocumentType to list of extensions
        """
        result: Dict[DocumentType, list] = {}

        for ext, doc_type in cls.EXTENSION_MAP.items():
            if doc_type not in result:
                result[doc_type] = []
            result[doc_type].append(ext)

        return result
