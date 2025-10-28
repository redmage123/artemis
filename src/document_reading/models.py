#!/usr/bin/env python3
"""
WHY: Data models for document reading system.
RESPONSIBILITY: Define document types, parsed content structures, and type enumerations.
PATTERNS: Dataclass pattern for immutable data structures, Enum for document type constants.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


class DocumentType(Enum):
    """
    WHY: Enumeration of supported document formats.
    RESPONSIBILITY: Provide type-safe document format identifiers.
    """
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    ODT = "odt"
    ODS = "ods"
    TEXT = "text"
    MARKDOWN = "markdown"
    CSV = "csv"
    HTML = "html"
    JUPYTER = "jupyter"
    UNKNOWN = "unknown"


@dataclass
class ParsedDocument:
    """
    WHY: Structured container for parsed document content and metadata.
    RESPONSIBILITY: Hold extracted text and metadata from any document type.
    """
    content: str
    document_type: DocumentType
    file_path: str
    metadata: Optional[Dict[str, Any]] = None

    def __len__(self) -> int:
        """Return character count of content"""
        return len(self.content)

    def is_empty(self) -> bool:
        """Check if document has no content"""
        return not self.content or not self.content.strip()


@dataclass
class NotebookSummary:
    """
    WHY: Structured summary of Jupyter notebook content.
    RESPONSIBILITY: Hold statistical information about notebook structure.
    """
    total_cells: int
    code_cells: int
    markdown_cells: int
    total_code_lines: int
    functions_defined: List[str]
    classes_defined: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'total_cells': self.total_cells,
            'code_cells': self.code_cells,
            'markdown_cells': self.markdown_cells,
            'total_code_lines': self.total_code_lines,
            'functions_defined': self.functions_defined,
            'classes_defined': self.classes_defined
        }
