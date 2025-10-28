#!/usr/bin/env python3
"""
Module: notebook_validator.py

WHY: Validates notebook structure and content before writing to disk.
     Ensures notebooks meet Jupyter format specifications.

RESPONSIBILITY:
- Validate notebook JSON structure
- Check cell format and metadata
- Verify required notebook fields
- Validate cell execution order
- Ensure notebook version compatibility

PATTERNS:
- Guard Clauses: Early returns for validation failures
- Strategy Pattern: Different validation rules per cell type
- Chain of Responsibility: Multiple validation steps
"""

from typing import Dict, Any, List, Optional, Tuple


class NotebookValidator:
    """
    Validate notebook structure and content

    WHY: Ensures generated notebooks are valid and executable
    RESPONSIBILITY: Verify notebook conforms to Jupyter specification
    """

    # Required notebook-level fields
    REQUIRED_NOTEBOOK_FIELDS: List[str] = [
        'cells',
        'metadata',
        'nbformat',
        'nbformat_minor'
    ]

    # Required cell fields
    REQUIRED_CELL_FIELDS: List[str] = [
        'cell_type',
        'metadata',
        'source'
    ]

    # Valid cell types
    VALID_CELL_TYPES: List[str] = ['code', 'markdown', 'raw']

    # Minimum/maximum supported nbformat versions
    MIN_NBFORMAT: int = 4
    MAX_NBFORMAT: int = 5

    def validate_notebook(
        self,
        notebook: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate complete notebook structure

        Time Complexity: O(n) where n = number of cells
        Space Complexity: O(1) constant space

        Args:
            notebook: Notebook dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if notebook is valid
            - error_message: None if valid, error string if invalid
        """
        # Guard clause: None input
        if notebook is None:
            return False, "Notebook is None"

        # Guard clause: not a dictionary
        if not isinstance(notebook, dict):
            return False, f"Notebook must be dict, got {type(notebook).__name__}"

        # Validate required fields
        is_valid, error = self._validate_required_fields(notebook)
        if not is_valid:
            return False, error

        # Validate nbformat version
        is_valid, error = self._validate_nbformat(notebook)
        if not is_valid:
            return False, error

        # Validate cells
        is_valid, error = self._validate_cells(notebook)
        if not is_valid:
            return False, error

        # Validate metadata
        is_valid, error = self._validate_metadata(notebook)
        if not is_valid:
            return False, error

        return True, None

    def _validate_required_fields(
        self,
        notebook: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate required notebook-level fields exist

        Time Complexity: O(n) where n = number of required fields
        Space Complexity: O(1) constant space

        Args:
            notebook: Notebook dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        for field in self.REQUIRED_NOTEBOOK_FIELDS:
            if field not in notebook:
                return False, f"Missing required field: {field}"

        return True, None

    def _validate_nbformat(
        self,
        notebook: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate nbformat version is supported

        Time Complexity: O(1) constant time
        Space Complexity: O(1) constant space

        Args:
            notebook: Notebook dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        nbformat = notebook.get('nbformat')

        # Guard clause: missing nbformat
        if nbformat is None:
            return False, "nbformat is required"

        # Guard clause: not an integer
        if not isinstance(nbformat, int):
            return False, f"nbformat must be int, got {type(nbformat).__name__}"

        # Guard clause: unsupported version
        if nbformat < self.MIN_NBFORMAT or nbformat > self.MAX_NBFORMAT:
            return False, f"nbformat {nbformat} not supported (must be {self.MIN_NBFORMAT}-{self.MAX_NBFORMAT})"

        return True, None

    def _validate_cells(
        self,
        notebook: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate all cells in notebook

        Time Complexity: O(n) where n = number of cells
        Space Complexity: O(1) constant space

        Args:
            notebook: Notebook dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        cells = notebook.get('cells', [])

        # Guard clause: not a list
        if not isinstance(cells, list):
            return False, f"cells must be list, got {type(cells).__name__}"

        # Validate each cell
        for i, cell in enumerate(cells):
            is_valid, error = self._validate_cell(cell, i)
            if not is_valid:
                return False, error

        return True, None

    def _validate_cell(
        self,
        cell: Dict[str, Any],
        index: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate single cell structure

        Time Complexity: O(1) constant time per cell
        Space Complexity: O(1) constant space

        Args:
            cell: Cell dictionary to validate
            index: Cell index in notebook (for error messages)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Guard clause: not a dictionary
        if not isinstance(cell, dict):
            return False, f"Cell {index} must be dict, got {type(cell).__name__}"

        # Validate required cell fields
        for field in self.REQUIRED_CELL_FIELDS:
            if field not in cell:
                return False, f"Cell {index} missing required field: {field}"

        # Validate cell type
        cell_type = cell.get('cell_type')
        if cell_type not in self.VALID_CELL_TYPES:
            return False, f"Cell {index} has invalid type: {cell_type}"

        # Validate source is list or string
        source = cell.get('source')
        if not isinstance(source, (list, str)):
            return False, f"Cell {index} source must be list or str, got {type(source).__name__}"

        # Validate code cell specific fields
        if cell_type == 'code':
            is_valid, error = self._validate_code_cell(cell, index)
            if not is_valid:
                return False, error

        return True, None

    def _validate_code_cell(
        self,
        cell: Dict[str, Any],
        index: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate code cell specific fields

        Time Complexity: O(1) constant time
        Space Complexity: O(1) constant space

        Args:
            cell: Code cell dictionary
            index: Cell index (for error messages)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Code cells should have execution_count and outputs
        if 'execution_count' not in cell:
            return False, f"Code cell {index} missing execution_count"

        if 'outputs' not in cell:
            return False, f"Code cell {index} missing outputs"

        # Outputs must be a list
        outputs = cell.get('outputs')
        if not isinstance(outputs, list):
            return False, f"Code cell {index} outputs must be list, got {type(outputs).__name__}"

        return True, None

    def _validate_metadata(
        self,
        notebook: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate notebook metadata

        Time Complexity: O(1) constant time
        Space Complexity: O(1) constant space

        Args:
            notebook: Notebook dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        metadata = notebook.get('metadata')

        # Guard clause: not a dictionary
        if not isinstance(metadata, dict):
            return False, f"metadata must be dict, got {type(metadata).__name__}"

        return True, None

    def validate_notebook_path(self, path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate notebook file path

        Time Complexity: O(1) constant time
        Space Complexity: O(1) constant space

        Args:
            path: File path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Guard clause: empty path
        if not path:
            return False, "Path is empty"

        # Guard clause: not a string
        if not isinstance(path, str):
            return False, f"Path must be str, got {type(path).__name__}"

        # Guard clause: wrong extension
        if not path.endswith('.ipynb'):
            return False, f"Path must end with .ipynb, got {path}"

        return True, None

    def get_validation_summary(
        self,
        notebook: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get detailed validation summary

        Time Complexity: O(n) where n = number of cells
        Space Complexity: O(n) for storing cell info

        Args:
            notebook: Notebook to summarize

        Returns:
            Dictionary with validation summary
        """
        is_valid, error = self.validate_notebook(notebook)

        summary = {
            'is_valid': is_valid,
            'error': error,
            'num_cells': len(notebook.get('cells', [])),
            'nbformat': notebook.get('nbformat'),
            'nbformat_minor': notebook.get('nbformat_minor'),
        }

        # Count cell types
        if is_valid:
            cells = notebook.get('cells', [])
            cell_type_counts = {}
            for cell in cells:
                cell_type = cell.get('cell_type', 'unknown')
                cell_type_counts[cell_type] = cell_type_counts.get(cell_type, 0) + 1
            summary['cell_type_counts'] = cell_type_counts

        return summary
