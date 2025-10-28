#!/usr/bin/env python3
"""
Output File Generator

WHY: Orchestrates generation of all output formats (JSON, Markdown, HTML, PDF).
RESPONSIBILITY: Coordinate file generation and manage output paths.
PATTERNS:
- Facade pattern (simplifies multiple generator calls)
- Single Responsibility
"""

import json
from pathlib import Path
from typing import Dict, Optional

from artemis_stage_interface import LoggerInterface
from ssd_generation.models.ssd_document import SSDDocument
from ssd_generation.generators.markdown_generator import MarkdownGenerator
from ssd_generation.generators.html_generator import HTMLGenerator
from ssd_generation.generators.pdf_generator import PDFGenerator


class OutputFileGenerator:
    """
    Orchestrates generation of all output formats

    WHY: Centralized file generation coordination.
    WHEN: Called during SSD generation to produce output files.
    """

    def __init__(
        self,
        output_dir: Path,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True
    ):
        """Initialize output file generator"""
        self.output_dir = output_dir
        self.logger = logger
        self.verbose = verbose

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize generators
        self.markdown_generator = MarkdownGenerator()
        self.html_generator = HTMLGenerator()
        self.pdf_generator = PDFGenerator(logger=logger, verbose=verbose)

    def generate_output_files(
        self,
        card_id: str,
        ssd_document: SSDDocument,
        include_pdf: bool = True
    ) -> Dict[str, str]:
        """
        Generate output files (JSON, Markdown, HTML, PDF)

        Args:
            card_id: Card identifier for file naming
            ssd_document: SSD document to generate
            include_pdf: Whether to attempt PDF generation

        Returns:
            Dict with file paths
        """
        file_paths = {}

        # 1. JSON output
        json_path = self.output_dir / f"ssd_{card_id}.json"
        with open(json_path, 'w') as f:
            json.dump(ssd_document.to_dict(), f, indent=2)
        file_paths['json'] = str(json_path)

        # 2. Markdown output
        markdown_path = self.output_dir / f"ssd_{card_id}.md"
        markdown_content = self.markdown_generator.generate_markdown(ssd_document)
        with open(markdown_path, 'w') as f:
            f.write(markdown_content)
        file_paths['markdown'] = str(markdown_path)

        # 3. HTML output (with embedded Chart.js for diagrams)
        html_path = self.output_dir / f"ssd_{card_id}.html"
        html_content = self.html_generator.generate_html(ssd_document)
        with open(html_path, 'w') as f:
            f.write(html_content)
        file_paths['html'] = str(html_path)

        # 4. PDF output (optional)
        if include_pdf:
            pdf_path = self.output_dir / f"ssd_{card_id}.pdf"
            generated_pdf = self.pdf_generator.generate_pdf(
                str(html_path),
                pdf_path
            )
            if generated_pdf:
                file_paths['pdf'] = str(generated_pdf)

        return file_paths
