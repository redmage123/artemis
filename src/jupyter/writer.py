#!/usr/bin/env python3
"""
WHY: Write Jupyter notebooks to disk in JSON format
RESPONSIBILITY: Serialize notebook structures to .ipynb files
PATTERNS:
- Single responsibility for file writing
- Guard clauses for validation
- Path normalization for cross-platform compatibility

This module handles all notebook output operations, ensuring notebooks
are written with proper formatting and structure.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any

from artemis_exceptions import (
    FileWriteError,
    create_wrapped_exception
)


class JupyterNotebookWriter:
    """
    WHY: Write and save Jupyter notebooks to disk
    RESPONSIBILITY: Save .ipynb files with proper formatting
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        WHY: Initialize notebook writer with optional logging
        RESPONSIBILITY: Store logger reference for operation tracking

        Args:
            logger: Optional logger instance
        """
        self.logger = logger

    def write_notebook(
        self,
        notebook: Dict[str, Any],
        file_path: str
    ) -> None:
        """
        WHY: Write Jupyter notebook to file with validation
        RESPONSIBILITY: Serialize notebook dict to JSON file

        Args:
            notebook: Notebook structure (from NotebookBuilder.build())
            file_path: Path where to save .ipynb file

        Raises:
            FileWriteError: If file cannot be written
        """
        try:
            path = Path(file_path)

            # Guard clause: Ensure .ipynb extension
            if path.suffix.lower() != '.ipynb':
                path = path.with_suffix('.ipynb')

            self._log(f"Writing Jupyter notebook: {path.name}", "INFO")

            # Create parent directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON with nice formatting
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2, ensure_ascii=False)

            self._log(f"Notebook saved: {path}", "SUCCESS")

        except Exception as e:
            raise create_wrapped_exception(
                e,
                FileWriteError,
                f"Failed to write notebook: {file_path}",
                context={'file_path': file_path}
            )

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
