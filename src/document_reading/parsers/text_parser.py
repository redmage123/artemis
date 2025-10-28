#!/usr/bin/env python3
"""
WHY: Plain text and CSV file parsing.
RESPONSIBILITY: Extract content from text-based formats (TXT, MD, CSV).
PATTERNS: Single Responsibility - focused on simple text formats only.
"""

import csv
from typing import List
from artemis_exceptions import DocumentReadError


class TextParser:
    """
    WHY: Parse plain text and markdown files.
    RESPONSIBILITY: Read UTF-8 encoded text files.
    """

    @staticmethod
    def parse(file_path: str) -> str:
        """
        WHY: Read plain text or markdown file.
        RESPONSIBILITY: Load entire file as UTF-8 text.

        Args:
            file_path: Path to text file

        Returns:
            File contents as string

        Raises:
            DocumentReadError: If file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise DocumentReadError(
                f"Error reading text file: {str(e)}",
                context={"file_path": file_path},
                original_exception=e
            )


class CSVParser:
    """
    WHY: Parse CSV files into readable text format.
    RESPONSIBILITY: Convert CSV rows to pipe-separated text.
    """

    @staticmethod
    def parse(file_path: str) -> str:
        """
        WHY: Read CSV and format as pipe-separated text.
        RESPONSIBILITY: Extract all rows and join with pipe separators.

        Args:
            file_path: Path to CSV file

        Returns:
            Formatted text with rows separated by pipes

        Raises:
            DocumentReadError: If file cannot be read
        """
        try:
            text_content: List[str] = []

            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)

                for row in csv_reader:
                    # Join row values with pipes for better readability
                    row_text = " | ".join([cell.strip() for cell in row if cell.strip()])
                    if row_text:
                        text_content.append(row_text)

            return "\n".join(text_content)

        except Exception as e:
            raise DocumentReadError(
                f"Error reading CSV file: {str(e)}",
                context={"file_path": file_path},
                original_exception=e
            )
