#!/usr/bin/env python3
"""
WHY: Document reading package - Multi-format document content extraction.
RESPONSIBILITY: Provide unified interface for reading various document formats.
PATTERNS: Facade pattern exposing simple API, Strategy pattern for format-specific parsing.

Supported formats:
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Microsoft Excel (.xlsx, .xls)
- LibreOffice Writer (.odt)
- LibreOffice Calc (.ods)
- Plain Text (.txt)
- Markdown (.md)
- CSV (.csv)
- HTML (.html, .htm)
- Jupyter Notebooks (.ipynb)
"""

from document_reading.models import DocumentType, ParsedDocument, NotebookSummary
from document_reading.format_detector import FormatDetector
from document_reading.content_extractor import ContentExtractor
from document_reading.reader_factory import ParserFactory

# Parsers (optional - usually accessed through factory)
from document_reading.parsers import (
    PDFParser,
    TextParser,
    CSVParser,
    MarkdownParser,
    HTMLParser,
    WordParser,
    ExcelParser,
    ODTParser,
    ODSParser,
    JupyterParser
)

__all__ = [
    # Main API
    'ContentExtractor',
    'DocumentType',
    'ParsedDocument',
    'NotebookSummary',

    # Utilities
    'FormatDetector',
    'ParserFactory',

    # Parsers (for advanced use)
    'PDFParser',
    'TextParser',
    'CSVParser',
    'MarkdownParser',
    'HTMLParser',
    'WordParser',
    'ExcelParser',
    'ODTParser',
    'ODSParser',
    'JupyterParser'
]

__version__ = '2.0.0'
