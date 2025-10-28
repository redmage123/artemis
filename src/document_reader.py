#!/usr/bin/env python3
"""
Document Reader - Backward Compatibility Wrapper

WHY: Maintain backward compatibility with existing code while delegating to
     refactored document_reading package.
RESPONSIBILITY: Re-export DocumentReader class with same API as original.
PATTERNS: Facade pattern - wrapper around new modular implementation.

This module provides backward compatibility for code using the old DocumentReader class.
All new code should import from document_reading package directly:
    from document_reading import ContentExtractor

Deprecated - Use document_reading.ContentExtractor instead.

Migration example:
    # Old:
    from document_reader import DocumentReader
    reader = DocumentReader(verbose=True)
    text = reader.read_document("file.pdf")

    # New:
    from document_reading import ContentExtractor
    extractor = ContentExtractor(verbose=True)
    text = extractor.extract_text("file.pdf")
"""

from typing import Dict, List
from document_reading import ContentExtractor


class DocumentReader:
    """
    Backward compatibility wrapper for ContentExtractor.

    WHY: Maintain API compatibility with legacy code.
    RESPONSIBILITY: Delegate all operations to ContentExtractor.
    PATTERNS: Adapter pattern - adapts new API to old interface.

    DEPRECATED: Use document_reading.ContentExtractor instead.

    This class provides the same interface as the original 701-line DocumentReader
    but delegates to the refactored modular document_reading package.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize Document Reader (Compatibility Wrapper).

        WHY: Maintain same constructor signature as original.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._extractor = ContentExtractor(verbose=verbose)

        # Maintain backward compatibility attributes
        self.has_pdf = self._check_parser_available('PDF')
        self.has_docx = self._check_parser_available('Microsoft Word')
        self.has_openpyxl = self._check_parser_available('Microsoft Excel')
        self.has_odf = self._check_parser_available('LibreOffice Writer')
        self.has_pypandoc = False  # Pypandoc not supported in new version

    def _check_parser_available(self, category: str) -> bool:
        """
        Check if parser for category is available.

        WHY: Maintain backward compatibility with availability checks.

        Args:
            category: Parser category name

        Returns:
            True if parser is available
        """
        try:
            supported = self._extractor.get_supported_formats()
            return category in supported
        except Exception:
            return False

    def read_document(self, file_path: str) -> str:
        """
        Read document and extract text content.

        WHY: Maintain same method signature as original.
        RESPONSIBILITY: Delegate to ContentExtractor.extract_text().

        Args:
            file_path: Path to document file

        Returns:
            Extracted text content

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
            DocumentReadError: If reading fails
        """
        return self._extractor.extract_text(file_path)

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get dictionary of supported formats based on available libraries.

        WHY: Maintain same method signature as original.
        RESPONSIBILITY: Delegate to ContentExtractor.

        Returns:
            Dict with categories and supported extensions
        """
        return self._extractor.get_supported_formats()

    def log(self, message: str):
        """
        Log message if verbose.

        WHY: Maintain same method signature as original.

        Args:
            message: Message to log
        """
        if self.verbose:
            print(f"[DocumentReader] {message}")


def main():
    """
    Test document reader (Compatibility Wrapper).

    WHY: Maintain same CLI interface as original.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Test document reader")
    parser.add_argument("file", help="File to read")
    args = parser.parse_args()

    reader = DocumentReader(verbose=True)

    print("\n📚 Supported Formats:")
    for category, extensions in reader.get_supported_formats().items():
        print(f"  {category}: {', '.join(extensions)}")

    print(f"\n📄 Reading: {args.file}\n")
    print("=" * 80)

    text = reader.read_document(args.file)
    print(text)

    print("=" * 80)
    print(f"\n✅ Extracted {len(text)} characters")


if __name__ == "__main__":
    main()
