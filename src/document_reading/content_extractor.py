from artemis_logger import get_logger
logger = get_logger('content_extractor')
'\nWHY: Unified document content extraction orchestrator.\nRESPONSIBILITY: Coordinate format detection, parser selection, and content extraction.\nPATTERNS: Facade pattern - simple interface over complex subsystem, Guard clauses.\n'
from pathlib import Path
from typing import Optional
from document_reading.models import DocumentType, ParsedDocument
from document_reading.format_detector import FormatDetector
from document_reading.reader_factory import ParserFactory
from artemis_exceptions import UnsupportedDocumentFormatError, DocumentReadError, wrap_exception

class ContentExtractor:
    """
    WHY: High-level interface for extracting content from any supported document.
    RESPONSIBILITY: Orchestrate format detection, parser creation, and content extraction.
    """

    def __init__(self, verbose: bool=False):
        """
        WHY: Initialize extractor with dependencies.
        RESPONSIBILITY: Create factory for parser instantiation.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.factory = ParserFactory(verbose=verbose)
        self.format_detector = FormatDetector()

    def extract(self, file_path: str) -> ParsedDocument:
        """
        WHY: Extract content from document file.
        RESPONSIBILITY: Detect format, create parser, extract content, return structured result.

        Args:
            file_path: Path to document file

        Returns:
            ParsedDocument with content and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            UnsupportedDocumentFormatError: If format is not supported
            DocumentReadError: If extraction fails
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f'File not found: {file_path}')
            document_type = self.format_detector.detect_from_path(file_path)
            extension = self.format_detector.get_extension(file_path)
            if self.verbose:
                
                logger.log(f'[ContentExtractor] Reading {extension} file: {path.name}', 'INFO')
            if document_type == DocumentType.UNKNOWN:
                raise UnsupportedDocumentFormatError(f'Unsupported file format: {extension}', context={'file_path': file_path, 'extension': extension})
            parser = self.factory.create_parser(document_type)
            if hasattr(parser, 'is_available') and (not parser.is_available()):
                raise DocumentReadError(f'Parser for {document_type.value} not available (missing dependencies)', context={'file_path': file_path, 'document_type': str(document_type)})
            content = parser.parse(file_path)
            return ParsedDocument(content=content, document_type=document_type, file_path=str(path.absolute()), metadata={'extension': extension, 'file_name': path.name, 'file_size': path.stat().st_size})
        except FileNotFoundError:
            raise
        except UnsupportedDocumentFormatError:
            raise
        except DocumentReadError:
            raise
        except Exception as e:
            raise wrap_exception(e, DocumentReadError, f'Error extracting content from: {file_path}', context={'file_path': file_path})

    def extract_text(self, file_path: str) -> str:
        """
        WHY: Convenience method to extract just the text content.
        RESPONSIBILITY: Extract and return only the text, not full ParsedDocument.

        Args:
            file_path: Path to document file

        Returns:
            Extracted text content

        Raises:
            Same as extract()
        """
        parsed_doc = self.extract(file_path)
        return parsed_doc.content

    def get_supported_formats(self) -> dict:
        """
        WHY: Report which document formats are currently supported.
        RESPONSIBILITY: Query all parsers for availability status.

        Returns:
            Dictionary of supported formats grouped by category
        """
        supported = {'Always Supported': ['.txt', '.md', '.markdown', '.csv', '.ipynb']}
        parser_checks = {'PDF': (DocumentType.PDF, ['.pdf']), 'Microsoft Word': (DocumentType.WORD, ['.docx', '.doc']), 'Microsoft Excel': (DocumentType.EXCEL, ['.xlsx', '.xls']), 'LibreOffice Writer': (DocumentType.ODT, ['.odt']), 'LibreOffice Calc': (DocumentType.ODS, ['.ods']), 'HTML': (DocumentType.HTML, ['.html', '.htm'])}
        for category, (doc_type, extensions) in parser_checks.items():
            try:
                parser = self.factory.create_parser(doc_type)
                if hasattr(parser, 'is_available') and parser.is_available():
                    supported[category] = extensions
            except Exception:
                pass
        return supported

    def log(self, message: str) -> None:
        """
        WHY: Centralized logging method.
        RESPONSIBILITY: Print log message if verbose is enabled.

        Args:
            message: Message to log
        """
        if self.verbose:
            
            logger.log(f'[ContentExtractor] {message}', 'INFO')