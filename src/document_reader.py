from artemis_logger import get_logger
logger = get_logger('document_reader')
'\nDocument Reader - Backward Compatibility Wrapper\n\nWHY: Maintain backward compatibility with existing code while delegating to\n     refactored document_reading package.\nRESPONSIBILITY: Re-export DocumentReader class with same API as original.\nPATTERNS: Facade pattern - wrapper around new modular implementation.\n\nThis module provides backward compatibility for code using the old DocumentReader class.\nAll new code should import from document_reading package directly:\n    from document_reading import ContentExtractor\n\nDeprecated - Use document_reading.ContentExtractor instead.\n\nMigration example:\n    # Old:\n    from document_reader import DocumentReader\n    reader = DocumentReader(verbose=True)\n    text = reader.read_document("file.pdf")\n\n    # New:\n    from document_reading import ContentExtractor\n    extractor = ContentExtractor(verbose=True)\n    text = extractor.extract_text("file.pdf")\n'
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

    def __init__(self, verbose: bool=True):
        """
        Initialize Document Reader (Compatibility Wrapper).

        WHY: Maintain same constructor signature as original.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._extractor = ContentExtractor(verbose=verbose)
        self.has_pdf = self._check_parser_available('PDF')
        self.has_docx = self._check_parser_available('Microsoft Word')
        self.has_openpyxl = self._check_parser_available('Microsoft Excel')
        self.has_odf = self._check_parser_available('LibreOffice Writer')
        self.has_pypandoc = False

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
            
            logger.log(f'[DocumentReader] {message}', 'INFO')

def main():
    """
    Test document reader (Compatibility Wrapper).

    WHY: Maintain same CLI interface as original.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Test document reader')
    parser.add_argument('file', help='File to read')
    args = parser.parse_args()
    reader = DocumentReader(verbose=True)
    
    logger.log('\n📚 Supported Formats:', 'INFO')
    for category, extensions in reader.get_supported_formats().items():
        
        logger.log(f"  {category}: {', '.join(extensions)}", 'INFO')
    
    logger.log(f'\n📄 Reading: {args.file}\n', 'INFO')
    
    logger.log('=' * 80, 'INFO')
    text = reader.read_document(args.file)
    
    logger.log(text, 'INFO')
    
    logger.log('=' * 80, 'INFO')
    
    logger.log(f'\n✅ Extracted {len(text)} characters', 'INFO')
if __name__ == '__main__':
    main()