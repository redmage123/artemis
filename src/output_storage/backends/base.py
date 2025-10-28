#!/usr/bin/env python3
"""
WHY: Define common interface for all storage backends
RESPONSIBILITY: Provide abstract base class for storage operations
PATTERNS: Strategy (polymorphic backends), Template Method (common interface)

StorageBackend defines:
- write_file() - Write content to storage
- read_file() - Read content from storage
- list_files() - List files with prefix
- delete_file() - Delete file from storage
- get_full_path() - Get full path/URI
"""

from abc import ABC, abstractmethod
from typing import List


class StorageBackend(ABC):
    """
    Abstract base class for storage backends

    All storage backends (local, S3, GCS) must implement this interface.
    """

    @abstractmethod
    def write_file(self, relative_path: str, content: str) -> str:
        """
        Write content to a file

        Args:
            relative_path: Path relative to base storage location
            content: File content

        Returns:
            Full path or URI of written file
        """
        pass

    @abstractmethod
    def read_file(self, relative_path: str) -> str:
        """
        Read content from a file

        Args:
            relative_path: Path relative to base storage location

        Returns:
            File content
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files with given prefix

        Args:
            prefix: Prefix to filter files

        Returns:
            List of relative file paths
        """
        pass

    @abstractmethod
    def delete_file(self, relative_path: str) -> bool:
        """
        Delete a file

        Args:
            relative_path: Path relative to base storage location

        Returns:
            True if file was deleted, False otherwise
        """
        pass

    @abstractmethod
    def get_full_path(self, relative_path: str) -> str:
        """
        Get full path/URI for a relative path

        Args:
            relative_path: Path relative to base storage location

        Returns:
            Full path or URI (e.g., /full/path or s3://bucket/path)
        """
        pass
