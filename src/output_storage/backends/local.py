#!/usr/bin/env python3
"""
WHY: Provide local filesystem storage backend
RESPONSIBILITY: Implement storage operations using local filesystem
PATTERNS: Strategy (storage backend), Guard Clauses (validation)

LocalStorageBackend provides:
- Filesystem-based storage (default)
- Automatic directory creation
- Permission management
- Relative to absolute path conversion
"""

import os
from pathlib import Path
from typing import List
from output_storage.backends.base import StorageBackend


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem storage backend

    Stores all outputs in a local directory tree.
    """

    def __init__(self, base_path: str = "../../outputs"):
        """
        Initialize local storage backend

        Args:
            base_path: Base path for storage (absolute or relative)
        """
        # Convert relative paths to absolute
        if not Path(base_path).is_absolute():
            # Resolve relative to the current file's directory
            current_dir = Path(__file__).parent.parent.parent
            base_path = (current_dir / base_path).resolve()

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Try to set proper permissions
        try:
            os.chmod(self.base_path, 0o755)
        except PermissionError:
            pass

    def write_file(self, relative_path: str, content: str) -> str:
        """
        Write file to local storage

        Args:
            relative_path: Path relative to base
            content: File content

        Returns:
            Full filesystem path
        """
        full_path = self.base_path / relative_path

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        with open(full_path, 'w') as f:
            f.write(content)

        return str(full_path)

    def read_file(self, relative_path: str) -> str:
        """
        Read file from local storage

        Args:
            relative_path: Path relative to base

        Returns:
            File content
        """
        full_path = self.base_path / relative_path
        with open(full_path, 'r') as f:
            return f.read()

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files with given prefix

        Args:
            prefix: Prefix to filter files

        Returns:
            List of relative file paths
        """
        search_path = self.base_path / prefix if prefix else self.base_path

        # Guard clause - check if path exists
        if not search_path.exists():
            return []

        files = []

        # Recursively find all files
        for path in search_path.rglob("*"):
            # Guard clause - only include files
            if not path.is_file():
                continue

            relative = path.relative_to(self.base_path)
            files.append(str(relative))

        return sorted(files)

    def delete_file(self, relative_path: str) -> bool:
        """
        Delete file from local storage

        Args:
            relative_path: Path relative to base

        Returns:
            True if file was deleted, False otherwise
        """
        full_path = self.base_path / relative_path

        # Guard clause - check if file exists
        if not full_path.exists():
            return False

        full_path.unlink()
        return True

    def get_full_path(self, relative_path: str) -> str:
        """
        Get full filesystem path

        Args:
            relative_path: Path relative to base

        Returns:
            Full filesystem path
        """
        return str(self.base_path / relative_path)
