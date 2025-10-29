from artemis_logger import get_logger
logger = get_logger('document_reader_new')
'\nWHY: Backward compatibility wrapper for legacy DocumentReader API.\nRESPONSIBILITY: Maintain existing API while delegating to new modular system.\nPATTERNS: Adapter pattern - wraps new ContentExtractor to match old DocumentReader interface.\n\nThis wrapper ensures all existing code using DocumentReader continues to work\nwithout modification while benefiting from the new modular architecture.\n'
from typing import Dict, List
from pathlib import Path
from document_reading import ContentExtractor, DocumentType
from artemis_exceptions import UnsupportedDocumentFormatError, DocumentReadError

class DocumentReader:
    """
    WHY: Legacy API compatibility wrapper.
    RESPONSIBILITY: Provide backward-compatible interface to new document reading system.

    This class maintains the exact same API as the original DocumentReader,
    but delegates all work to the new modular ContentExtractor system.
    """
    EXTENSION_HANDLERS = {'.pdf': '_read_pdf', '.docx': '_read_word', '.doc': '_read_word', '.xlsx': '_read_excel', '.xls': '_read_excel', '.odt': '_read_odt', '.ods': '_read_ods', '.txt': '_read_text', '.md': '_read_text', '.markdown': '_read_text', '.csv': '_read_csv', '.html': '_read_html', '.htm': '_read_html', '.ipynb': '_read_ipynb'}

    def __init__(self, verbose: bool=True):
        """
        WHY: Initialize with same signature as original.
        RESPONSIBILITY: Create new ContentExtractor and mirror old API.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.extractor = ContentExtractor(verbose=verbose)
        self._set_compatibility_flags()

    def _set_compatibility_flags(self) -> None:
        """
        WHY: Set library availability flags for backward compatibility.
        RESPONSIBILITY: Mirror the old has_* flags from original DocumentReader.
        """
        from document_reading import PDFParser, WordParser, ExcelParser, ODTParser, HTMLParser
        self.has_pdf = PDFParser(verbose=False).is_available()
        self.has_docx = WordParser(verbose=False).is_available()
        self.has_openpyxl = ExcelParser(verbose=False).is_available()
        self.has_odf = ODTParser(verbose=False).is_available()
        try:
            from bs4 import BeautifulSoup
            self.has_bs4 = True
        except ImportError:
            self.has_bs4 = False
        try:
            import pypandoc
            self.has_pypandoc = True
        except ImportError:
            self.has_pypandoc = False
        if self.has_pdf:
            parser = PDFParser(verbose=False)
            self.pdf_library = parser.library

    def read_document(self, file_path: str) -> str:
        """
        WHY: Main entry point - same signature as original.
        RESPONSIBILITY: Delegate to ContentExtractor and return text content.

        Args:
            file_path: Path to document file

        Returns:
            Extracted text content

        Raises:
            ValueError: If file format is not supported (for backward compatibility)
            FileNotFoundError: If file doesn't exist
        """
        try:
            return self.extractor.extract_text(file_path)
        except UnsupportedDocumentFormatError as e:
            raise ValueError(str(e))

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        WHY: Report supported formats - same signature as original.
        RESPONSIBILITY: Delegate to ContentExtractor and format result.

        Returns:
            Dict with categories and supported extensions
        """
        return self.extractor.get_supported_formats()

    def log(self, message: str) -> None:
        """
        WHY: Logging method - same signature as original.
        RESPONSIBILITY: Print message if verbose enabled.

        Args:
            message: Message to log
        """
        if self.verbose:
            
            logger.log(f'[DocumentReader] {message}', 'INFO')

def main():
    """
    WHY: Test document reader - same as original.
    RESPONSIBILITY: Provide CLI for testing document reading.
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