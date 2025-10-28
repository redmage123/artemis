#!/usr/bin/env python3
"""
PDF Generator

WHY: Generates PDF representation of SSD documents from HTML.
RESPONSIBILITY: Convert HTML to PDF using weasyprint.
PATTERNS:
- Guard clauses (Pattern #10) for dependency checking
- Single Responsibility
"""

from pathlib import Path
from typing import Optional

from artemis_stage_interface import LoggerInterface


class PDFGenerator:
    """
    Generates PDF from HTML using weasyprint

    WHY: Produces professional PDF documentation from HTML.
    WHEN: Called during output generation to create .pdf files.
    """

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True
    ):
        """Initialize PDF generator"""
        self.logger = logger
        self.verbose = verbose

    def generate_pdf(
        self,
        html_path: str,
        output_path: Path
    ) -> Optional[Path]:
        """
        Generate PDF from HTML using weasyprint

        Pattern #10: Guard clauses for dependency checking

        Args:
            html_path: Path to HTML file
            output_path: Path where PDF should be saved

        Returns:
            Path to PDF if successful, None otherwise
        """
        # Guard clause: Check if PDF generation dependencies available
        try:
            from weasyprint import HTML
        except ImportError:
            if self.verbose and self.logger:
                self.logger.log(
                    "⚠️  PDF generation skipped (weasyprint not installed)",
                    "WARNING"
                )
            return None

        # Guard clause: Check HTML file exists
        if not Path(html_path).exists():
            if self.verbose and self.logger:
                self.logger.log("⚠️  PDF generation skipped (HTML file not found)", "WARNING")
            return None

        try:
            if self.verbose and self.logger:
                self.logger.log("📄 Generating PDF...", "INFO")

            # Generate PDF from HTML
            HTML(filename=html_path).write_pdf(output_path)

            if self.verbose and self.logger:
                self.logger.log(f"   PDF generated: {output_path}", "SUCCESS")

            return output_path

        except Exception as e:
            if self.verbose and self.logger:
                self.logger.log(f"⚠️  PDF generation failed: {e}", "WARNING")
            return None
