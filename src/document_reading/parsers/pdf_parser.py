from artemis_logger import get_logger
logger = get_logger('pdf_parser')
'\nWHY: PDF document parsing using PyPDF2 or pdfplumber libraries.\nRESPONSIBILITY: Extract text content from PDF files with library auto-detection.\nPATTERNS: Strategy pattern for multiple PDF library support, Guard clauses for validation.\n'
from typing import List, Optional
from artemis_exceptions import DocumentReadError

class PDFParser:
    """
    WHY: Dedicated PDF parsing with support for multiple libraries.
    RESPONSIBILITY: Extract text from PDF using best available library.
    """

    def __init__(self, verbose: bool=False):
        """
        WHY: Initialize parser with library detection.
        RESPONSIBILITY: Check which PDF libraries are available.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.library: Optional[str] = None
        self._detect_library()

    def _detect_library(self) -> None:
        """
        WHY: Auto-detect available PDF parsing library.
        RESPONSIBILITY: Set self.library to 'PyPDF2', 'pdfplumber', or None.
        """
        try:
            import PyPDF2
            self.library = 'PyPDF2'
            return
        except ImportError:
            pass
        try:
            import pdfplumber
            self.library = 'pdfplumber'
            return
        except ImportError:
            pass
        if self.verbose:
            
            logger.log('[PDFParser] No PDF library available. Install: pip install PyPDF2 or pdfplumber', 'INFO')

    def is_available(self) -> bool:
        """
        WHY: Check if PDF parsing is available.
        RESPONSIBILITY: Return True if any PDF library was detected.

        Returns:
            True if PDF parsing is supported
        """
        return self.library is not None

    def parse(self, file_path: str) -> str:
        """
        WHY: Extract text from PDF file.
        RESPONSIBILITY: Read PDF and return combined text from all pages.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            DocumentReadError: If library not available or parsing fails
        """
        if not self.is_available():
            raise DocumentReadError('PDF support not available. Install: pip install PyPDF2 or pdfplumber', context={'file_path': file_path})
        if self.library == 'PyPDF2':
            return self._parse_with_pypdf2(file_path)
        elif self.library == 'pdfplumber':
            return self._parse_with_pdfplumber(file_path)
        raise DocumentReadError(f'Unknown PDF library: {self.library}', context={'file_path': file_path, 'library': self.library})

    def _parse_with_pypdf2(self, file_path: str) -> str:
        """
        WHY: Parse PDF using PyPDF2 library.
        RESPONSIBILITY: Extract text from all pages using PyPDF2.

        Args:
            file_path: Path to PDF file

        Returns:
            Combined text from all pages
        """
        import PyPDF2
        text_content: List[str] = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
        return '\n'.join(text_content)

    def _parse_with_pdfplumber(self, file_path: str) -> str:
        """
        WHY: Parse PDF using pdfplumber library.
        RESPONSIBILITY: Extract text from all pages using pdfplumber.

        Args:
            file_path: Path to PDF file

        Returns:
            Combined text from all pages
        """
        import pdfplumber
        text_content: List[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return '\n'.join(text_content)