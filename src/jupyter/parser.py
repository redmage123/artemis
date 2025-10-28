#!/usr/bin/env python3
"""
WHY: Parse Jupyter notebook JSON files into Python objects
RESPONSIBILITY: Read .ipynb files and extract cells with validation
PATTERNS:
- Single responsibility for file reading/parsing
- Guard clauses for validation
- Strategy pattern for cell type extraction

This module handles all notebook file I/O and parsing operations,
transforming JSON structures into NotebookCell objects.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from artemis_exceptions import (
    FileReadError,
    create_wrapped_exception
)

from .models import NotebookCell, CellType


class JupyterNotebookReader:
    """
    WHY: Read and parse Jupyter notebooks from disk
    RESPONSIBILITY: Parse .ipynb files and validate structure
    PERFORMANCE: Single-pass parsing - O(n) where n=cells
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        WHY: Initialize notebook reader with optional logging
        RESPONSIBILITY: Store logger reference for operation tracking

        Args:
            logger: Optional logger instance
        """
        self.logger = logger

    def read_notebook(self, file_path: str) -> Dict[str, Any]:
        """
        WHY: Read Jupyter notebook file and validate format
        RESPONSIBILITY: Load JSON and ensure valid notebook structure
        PERFORMANCE: Single-pass validation with guard clauses

        Args:
            file_path: Path to .ipynb file

        Returns:
            Parsed notebook structure

        Raises:
            FileReadError: If file cannot be read or parsed
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        try:
            path = Path(file_path)

            # Guard clause: Validate file exists early
            if not path.exists():
                raise FileNotFoundError(
                    f"Notebook file not found: {file_path}"
                )

            # Guard clause: Validate file extension early
            if path.suffix.lower() != '.ipynb':
                raise ValueError(
                    f"File must have .ipynb extension: {file_path}"
                )

            self._log(f"Reading Jupyter notebook: {path.name}", "INFO")

            # Read and parse JSON
            with open(path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            # Guard clause: Validate notebook format early
            if 'cells' not in notebook:
                raise ValueError(
                    f"Invalid notebook format: missing 'cells' key"
                )

            cell_count = len(notebook['cells'])
            self._log(f"Read notebook with {cell_count} cells", "INFO")

            return notebook

        except FileNotFoundError:
            raise  # Re-raise as-is (already formatted correctly)
        except json.JSONDecodeError as e:
            raise create_wrapped_exception(
                e,
                FileReadError,
                f"Failed to parse notebook JSON: {file_path}",
                context={'file_path': file_path}
            )
        except Exception as e:
            raise create_wrapped_exception(
                e,
                FileReadError,
                f"Failed to read notebook: {file_path}",
                context={'file_path': file_path}
            )

    def _extract_cells_by_type(
        self,
        notebook: Dict[str, Any],
        cell_type: str
    ) -> List[NotebookCell]:
        """
        WHY: Extract cells of specific type (DRY helper)
        RESPONSIBILITY: Filter and convert cells to NotebookCell objects
        PERFORMANCE: Single-pass filter - O(n) where n = number of cells

        Args:
            notebook: Parsed notebook structure
            cell_type: Type of cells to extract ('code', 'markdown', etc.)

        Returns:
            List of cells matching the type
        """
        # Guard clause: Handle missing cells early
        cells_data = notebook.get('cells', [])
        if not cells_data:
            return []

        # List comprehension for performance (faster than loop with append)
        is_code = cell_type == CellType.CODE.value

        return [
            NotebookCell(
                cell_type=cell_data['cell_type'],
                source=cell_data.get('source', []),
                metadata=cell_data.get('metadata', {}),
                outputs=cell_data.get('outputs', []) if is_code else [],
                execution_count=cell_data.get('execution_count') if is_code else None
            )
            for cell_data in cells_data
            if cell_data.get('cell_type') == cell_type
        ]

    def extract_code_cells(
        self,
        notebook: Dict[str, Any]
    ) -> List[NotebookCell]:
        """
        WHY: Public API for extracting code cells
        RESPONSIBILITY: Delegate to DRY helper method
        PERFORMANCE: Single-pass filter - O(n)

        Args:
            notebook: Parsed notebook structure

        Returns:
            List of code cells
        """
        return self._extract_cells_by_type(notebook, CellType.CODE.value)

    def extract_markdown_cells(
        self,
        notebook: Dict[str, Any]
    ) -> List[NotebookCell]:
        """
        WHY: Public API for extracting markdown cells
        RESPONSIBILITY: Delegate to DRY helper method
        PERFORMANCE: Single-pass filter - O(n)

        Args:
            notebook: Parsed notebook structure

        Returns:
            List of markdown cells
        """
        return self._extract_cells_by_type(notebook, CellType.MARKDOWN.value)

    def get_notebook_summary(self, notebook: Dict[str, Any]) -> Dict[str, Any]:
        """
        WHY: Get quick overview of notebook structure
        RESPONSIBILITY: Analyze cells and provide statistics
        PERFORMANCE: Single-pass analysis - O(n) where n = number of cells
        PATTERN: Dispatch table for cell type handling

        Args:
            notebook: Parsed notebook structure

        Returns:
            Dict with cell counts, code analysis, etc.
        """
        cells = notebook.get('cells', [])

        # Initialize summary structure
        summary = {
            'total_cells': len(cells),
            'code_cells': 0,
            'markdown_cells': 0,
            'raw_cells': 0,
            'total_code_lines': 0,
            'functions_defined': [],
            'classes_defined': [],
            'has_plotting': False
        }

        # Dispatch table: Map cell types to handler functions
        # WHY: Avoids if/elif chain, follows Open/Closed principle
        handlers = self._create_cell_handlers(summary)

        # Single pass through cells using dispatch table (O(n))
        for cell_data in cells:
            cell_type = cell_data.get('cell_type')

            # O(1) handler lookup and execution
            handler = handlers.get(cell_type)
            if handler:
                handler(cell_data)

        return summary

    def _create_cell_handlers(
        self,
        summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        WHY: Create dispatch table for cell type handling
        RESPONSIBILITY: Map cell types to processing functions

        Args:
            summary: Summary dict to update

        Returns:
            Dict mapping cell types to handler functions
        """
        return {
            CellType.CODE.value: lambda cd: self._process_code_cell(cd, summary),
            CellType.MARKDOWN.value: lambda _: self._increment_count(summary, 'markdown_cells'),
            'raw': lambda _: self._increment_count(summary, 'raw_cells')
        }

    def _process_code_cell(
        self,
        cell_data: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> None:
        """
        WHY: Process code cell for summary statistics (DRY helper)
        RESPONSIBILITY: Analyze code and update summary

        Args:
            cell_data: Cell data from notebook
            summary: Summary dict to update (modified in place)
        """
        summary['code_cells'] += 1

        # Analyze code cell
        cell = NotebookCell(
            cell_type=cell_data.get('cell_type'),
            source=cell_data.get('source', []),
            metadata=cell_data.get('metadata', {})
        )
        analysis = cell.analyze_code()

        # Update summary with analysis results
        summary['total_code_lines'] += analysis.get('line_count', 0)
        summary['functions_defined'].extend(analysis.get('functions', []))
        summary['classes_defined'].extend(analysis.get('classes', []))

        # Track plotting presence
        if analysis.get('has_plotting'):
            summary['has_plotting'] = True

    def _increment_count(self, summary: Dict[str, Any], key: str) -> None:
        """
        WHY: Increment counter in summary dict
        RESPONSIBILITY: Update cell type count

        Args:
            summary: Summary dict to update
            key: Key to increment
        """
        summary[key] = summary[key] + 1

    def _log(self, message: str, level: str = "INFO") -> None:
        """
        WHY: Centralized logging helper
        RESPONSIBILITY: Log if logger available

        Args:
            message: Log message
            level: Log level
        """
        if self.logger:
            self.logger.log(message, level)
