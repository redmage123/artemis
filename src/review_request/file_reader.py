#!/usr/bin/env python3
"""
WHY: Read implementation files from directory for code review
RESPONSIBILITY: Scan directory for supported file types and load into ImplementationFile objects
PATTERNS: Factory Method (from_file_path), Repository Pattern (file access)

File reading provides:
- Recursive directory scanning
- Extension filtering (supported languages only)
- Batch file loading
- Relative path calculation
"""

from typing import List
from pathlib import Path
from review_request.models import ImplementationFile


class ImplementationFileReader:
    """
    Reads implementation files from directory

    Scans recursively for supported file types.
    """

    # Dispatch table: supported file extensions
    SUPPORTED_EXTENSIONS = [
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.html', '.css', '.java', '.go', '.rb',
        '.rs', '.cpp', '.c', '.h', '.sh',
        '.yaml', '.yml', '.json', '.md', '.sql',
        '.kt', '.swift', '.php', '.scala', '.r', '.pl'
    ]

    def read_files(self, implementation_dir: str) -> List[ImplementationFile]:
        """
        Read all implementation files from directory

        Args:
            implementation_dir: Directory containing implementation files

        Returns:
            List of ImplementationFile instances

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        impl_path = Path(implementation_dir)

        # Guard clause - check directory exists
        if not impl_path.exists():
            raise FileNotFoundError(f"Implementation directory not found: {implementation_dir}")

        # Use list comprehension to gather all files - Pythonic!
        files = [
            ImplementationFile.from_file_path(file_path, impl_path)
            for ext in self.SUPPORTED_EXTENSIONS
            for file_path in impl_path.rglob(f'*{ext}')
        ]

        return files

    def read_specific_files(
        self,
        implementation_dir: str,
        file_paths: List[str]
    ) -> List[ImplementationFile]:
        """
        Read specific files from directory

        Args:
            implementation_dir: Base directory
            file_paths: List of relative file paths

        Returns:
            List of ImplementationFile instances
        """
        impl_path = Path(implementation_dir)

        # Guard clause - check directory exists
        if not impl_path.exists():
            raise FileNotFoundError(f"Implementation directory not found: {implementation_dir}")

        files = []
        for relative_path in file_paths:
            file_path = impl_path / relative_path

            # Guard clause - check file exists
            if not file_path.exists():
                continue

            files.append(ImplementationFile.from_file_path(file_path, impl_path))

        return files


def read_implementation_files(implementation_dir: str) -> List[ImplementationFile]:
    """
    Convenience function to read all implementation files from a directory

    Args:
        implementation_dir: Directory containing implementation files

    Returns:
        List of ImplementationFile instances

    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    reader = ImplementationFileReader()
    return reader.read_files(implementation_dir)
