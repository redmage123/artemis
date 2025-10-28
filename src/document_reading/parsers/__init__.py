#!/usr/bin/env python3
"""
WHY: Parser package exports for document reading system.
RESPONSIBILITY: Provide clean imports for all parser classes.
PATTERNS: Package initialization with explicit exports.
"""

from document_reading.parsers.pdf_parser import PDFParser
from document_reading.parsers.text_parser import TextParser, CSVParser
from document_reading.parsers.markdown_parser import MarkdownParser
from document_reading.parsers.html_parser import HTMLParser
from document_reading.parsers.office_parser import (
    WordParser,
    ExcelParser,
    ODTParser,
    ODSParser
)
from document_reading.parsers.jupyter_parser import JupyterParser

__all__ = [
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
