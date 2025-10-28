#!/usr/bin/env python3
"""
WHY: Factory for creating document parsers based on document type.
RESPONSIBILITY: Instantiate appropriate parser for each document format.
PATTERNS: Factory Pattern with dispatch table for O(1) parser lookup.
"""

from typing import Dict, Callable, Optional, Any
from document_reading.models import DocumentType
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
from artemis_exceptions import UnsupportedDocumentFormatError


class ParserFactory:
    """
    WHY: Centralize parser creation logic.
    RESPONSIBILITY: Create appropriate parser instance for each document type.
    """

    def __init__(self, verbose: bool = False):
        """
        WHY: Initialize factory with configuration.
        RESPONSIBILITY: Set verbose flag for all created parsers.

        Args:
            verbose: Enable verbose logging in parsers
        """
        self.verbose = verbose

        # Dispatch table for parser creation (Factory Pattern)
        self._parser_map: Dict[DocumentType, Callable[[], Any]] = {
            DocumentType.PDF: lambda: PDFParser(verbose=self.verbose),
            DocumentType.WORD: lambda: WordParser(verbose=self.verbose),
            DocumentType.EXCEL: lambda: ExcelParser(verbose=self.verbose),
            DocumentType.ODT: lambda: ODTParser(verbose=self.verbose),
            DocumentType.ODS: lambda: ODSParser(verbose=self.verbose),
            DocumentType.TEXT: lambda: TextParser(),
            DocumentType.MARKDOWN: lambda: MarkdownParser(),
            DocumentType.CSV: lambda: CSVParser(),
            DocumentType.HTML: lambda: HTMLParser(verbose=self.verbose),
            DocumentType.JUPYTER: lambda: JupyterParser(verbose=self.verbose)
        }

    def create_parser(self, document_type: DocumentType) -> Any:
        """
        WHY: Create parser instance for given document type.
        RESPONSIBILITY: Look up and instantiate appropriate parser.

        Args:
            document_type: Type of document to parse

        Returns:
            Parser instance for the document type

        Raises:
            UnsupportedDocumentFormatError: If document type is not supported
        """
        # Guard: Check if document type is supported
        if document_type == DocumentType.UNKNOWN:
            raise UnsupportedDocumentFormatError(
                "Cannot create parser for unknown document type",
                context={"document_type": str(document_type)}
            )

        # Get parser creator from dispatch table
        parser_creator = self._parser_map.get(document_type)

        # Guard: Check if parser exists for this type
        if not parser_creator:
            raise UnsupportedDocumentFormatError(
                f"No parser available for document type: {document_type.value}",
                context={"document_type": str(document_type)}
            )

        return parser_creator()

    def is_supported(self, document_type: DocumentType) -> bool:
        """
        WHY: Check if document type is supported.
        RESPONSIBILITY: Validate document type has a parser.

        Args:
            document_type: Type to check

        Returns:
            True if document type is supported
        """
        return document_type in self._parser_map

    def get_supported_types(self) -> list:
        """
        WHY: Get list of all supported document types.
        RESPONSIBILITY: Return all document types with parsers.

        Returns:
            List of supported DocumentType values
        """
        return list(self._parser_map.keys())
