#!/usr/bin/env python3
"""
Module: execution_handler.py

WHY: Handles notebook writing and optional execution.
     Separates I/O operations from notebook generation logic.

RESPONSIBILITY:
- Write notebooks to disk using JupyterNotebookWriter
- Validate notebooks before writing
- Handle file I/O errors gracefully
- Optionally execute notebooks after generation
- Track execution results

PATTERNS:
- Guard Clauses: Early returns for validation failures
- Dependency Injection: Writer injected via constructor
- Single Responsibility: Only handles notebook I/O and execution
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from jupyter_notebook_handler import JupyterNotebookWriter


class ExecutionHandler:
    """
    Handle notebook writing and execution

    WHY: Centralizes notebook I/O and execution logic
    RESPONSIBILITY: Write notebooks to disk and optionally execute them
    """

    def __init__(
        self,
        writer: Optional[JupyterNotebookWriter] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize execution handler

        Args:
            writer: Optional JupyterNotebookWriter instance
            logger: Optional logger for diagnostic messages
        """
        self.writer = writer or JupyterNotebookWriter()
        self.logger = logger

    def write_notebook(
        self,
        notebook: Dict[str, Any],
        output_path: Path
    ) -> Tuple[bool, Optional[str]]:
        """
        Write notebook to disk

        Time Complexity: O(n) where n = notebook size
        Space Complexity: O(n) for JSON serialization

        Args:
            notebook: Notebook dictionary to write
            output_path: Output file path

        Returns:
            Tuple of (success, error_message)
            - success: True if written successfully
            - error_message: None if success, error string if failure
        """
        # Guard clause: None notebook
        if notebook is None:
            return False, "Notebook is None"

        # Guard clause: not a dictionary
        if not isinstance(notebook, dict):
            return False, f"Notebook must be dict, got {type(notebook).__name__}"

        # Guard clause: invalid path
        if not output_path:
            return False, "Output path is empty"

        try:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write notebook using writer
            self.writer.write_notebook(notebook, str(output_path))

            self._log(f"Notebook written to {output_path}", "INFO")
            return True, None

        except PermissionError as e:
            error_msg = f"Permission denied writing to {output_path}: {e}"
            self._log(error_msg, "ERROR")
            return False, error_msg

        except OSError as e:
            error_msg = f"OS error writing to {output_path}: {e}"
            self._log(error_msg, "ERROR")
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error writing notebook: {e}"
            self._log(error_msg, "ERROR")
            return False, error_msg

    def read_notebook(
        self,
        notebook_path: Path
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Read notebook from disk

        Time Complexity: O(n) where n = file size
        Space Complexity: O(n) for notebook data

        Args:
            notebook_path: Path to notebook file

        Returns:
            Tuple of (notebook, error_message)
            - notebook: Dict if success, None if failure
            - error_message: None if success, error string if failure
        """
        # Guard clause: path doesn't exist
        if not notebook_path.exists():
            return None, f"Notebook not found: {notebook_path}"

        # Guard clause: not a file
        if not notebook_path.is_file():
            return None, f"Path is not a file: {notebook_path}"

        try:
            import json
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            self._log(f"Notebook loaded from {notebook_path}", "INFO")
            return notebook, None

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in notebook: {e}"
            self._log(error_msg, "ERROR")
            return None, error_msg

        except Exception as e:
            error_msg = f"Error reading notebook: {e}"
            self._log(error_msg, "ERROR")
            return None, error_msg

    def verify_written_notebook(
        self,
        notebook_path: Path
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify notebook was written correctly

        Time Complexity: O(n) where n = file size
        Space Complexity: O(n) for reading file

        Args:
            notebook_path: Path to verify

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Guard clause: file doesn't exist
        if not notebook_path.exists():
            return False, f"Notebook file not found: {notebook_path}"

        # Guard clause: empty file
        if notebook_path.stat().st_size == 0:
            return False, f"Notebook file is empty: {notebook_path}"

        # Try to read and parse
        notebook, error = self.read_notebook(notebook_path)
        if error:
            return False, error

        # Basic structure validation
        if not isinstance(notebook, dict):
            return False, "Notebook is not a valid dictionary"

        if 'cells' not in notebook:
            return False, "Notebook missing 'cells' field"

        self._log(f"Notebook verified: {notebook_path}", "INFO")
        return True, None

    def get_notebook_info(
        self,
        notebook_path: Path
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a notebook file

        Time Complexity: O(n) where n = file size
        Space Complexity: O(n) for notebook data

        Args:
            notebook_path: Path to notebook

        Returns:
            Dict with notebook info, or None if error
        """
        # Guard clause: file doesn't exist
        if not notebook_path.exists():
            return None

        notebook, error = self.read_notebook(notebook_path)
        if error:
            return None

        # Extract info
        info = {
            'path': str(notebook_path),
            'size_bytes': notebook_path.stat().st_size,
            'num_cells': len(notebook.get('cells', [])),
            'nbformat': notebook.get('nbformat'),
            'nbformat_minor': notebook.get('nbformat_minor'),
        }

        # Count cell types
        cells = notebook.get('cells', [])
        cell_type_counts = {}
        for cell in cells:
            cell_type = cell.get('cell_type', 'unknown')
            cell_type_counts[cell_type] = cell_type_counts.get(cell_type, 0) + 1
        info['cell_type_counts'] = cell_type_counts

        return info

    def execute_notebook(
        self,
        notebook_path: Path,
        timeout: int = 600
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute notebook using nbconvert or papermill

        Time Complexity: O(n) where n = execution time
        Space Complexity: O(1) constant space

        Note: This is a placeholder for notebook execution functionality.
              Full implementation would require nbconvert or papermill.

        Args:
            notebook_path: Path to notebook to execute
            timeout: Maximum execution time in seconds

        Returns:
            Tuple of (success, error_message)
        """
        # Guard clause: file doesn't exist
        if not notebook_path.exists():
            return False, f"Notebook not found: {notebook_path}"

        self._log(
            f"Notebook execution not implemented. Would execute: {notebook_path}",
            "WARNING"
        )

        # Placeholder - actual implementation would use:
        # import papermill as pm
        # pm.execute_notebook(
        #     str(notebook_path),
        #     str(notebook_path),
        #     timeout=timeout
        # )

        return True, None

    def _log(self, message: str, level: str = "INFO"):
        """
        Log message using logger or print

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        if self.logger:
            self.logger.log(message, level)
        else:
            print(f"[{level}] {message}")
