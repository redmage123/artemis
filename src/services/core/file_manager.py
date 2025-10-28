#!/usr/bin/env python3
"""
Module: services.core.file_manager

WHY: Centralizes all file operations to enable mocking in tests, consistent
     error handling, and a single point of control for file I/O operations.
     Prevents scattered file handling code across the codebase.

RESPONSIBILITY: Handle file I/O operations with consistent error handling and encoding.

PATTERNS:
- Single Responsibility: Only handles file I/O operations
- Static Methods: Stateless operations (no instance state needed)
- Template Method: Common error handling pattern across all operations
- Facade: Simplifies complex file operations (JSON, text, binary)
- Guard Clauses: Early return on validation failures

DESIGN DECISIONS:
- Static methods (no state, can be used without instantiation)
- Consistent error propagation (let exceptions bubble up with context)
- UTF-8 encoding by default (modern standard, handles most cases)
- Pathlib support (modern, cross-platform path handling)
- JSON indent=2 (human-readable, version control friendly)
- mkdir with parents=True (automatic parent directory creation)

Dependencies: None (uses only Python standard library)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class FileManager:
    """
    File I/O operations service with consistent error handling.

    WHAT: Provides simple, safe file I/O operations with standard encoding.
    WHY: Centralizes file operations for easier mocking and testing.

    Note: All methods are static - no instance state required.

    Example:
        >>> FileManager.write_text(Path("output.txt"), "Hello, World!")
        >>> content = FileManager.read_text(Path("output.txt"))
        >>> print(content)
        Hello, World!
    """

    # Encoding constants
    DEFAULT_ENCODING: str = "utf-8"
    JSON_INDENT: int = 2

    # JSON operations (dispatch table for custom encoders)
    JSON_ENCODERS: Dict[str, Any] = {}

    @staticmethod
    def read_json(file_path: Union[Path, str]) -> Dict:
        """
        Read and parse JSON file.

        WHAT: Reads and parses JSON file into Python dictionary.
        WHY: Encapsulates JSON parsing logic and provides single point for error handling.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
            PermissionError: If file can't be read

        Example:
            >>> config = FileManager.read_json("config.json")
            >>> print(config['version'])
        """
        # Ensure Path object
        path = Path(file_path)

        # Guard clause: Check file exists
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        # Guard clause: Check is file (not directory)
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        # Read and parse JSON
        with open(path, 'r', encoding=FileManager.DEFAULT_ENCODING) as f:
            return json.load(f)

    @staticmethod
    def write_json(
        file_path: Union[Path, str],
        data: Dict,
        indent: Optional[int] = JSON_INDENT
    ) -> None:
        """
        Write dictionary to JSON file with formatting.

        WHAT: Serializes dictionary to JSON and writes to file with indentation.
        WHY: Consistent JSON formatting (2-space indent) makes files human-readable
             and git-friendly.

        Args:
            file_path: Path to JSON file
            data: Dictionary to serialize
            indent: Number of spaces for indentation (default: 2, None for compact)

        Raises:
            TypeError: If data is not JSON serializable
            PermissionError: If file can't be written

        Example:
            >>> data = {"name": "Artemis", "version": "1.0"}
            >>> FileManager.write_json("metadata.json", data)
        """
        # Ensure Path object
        path = Path(file_path)

        # Ensure parent directory exists
        FileManager.ensure_directory(path.parent)

        # Write JSON with formatting
        with open(path, 'w', encoding=FileManager.DEFAULT_ENCODING) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def read_text(file_path: Union[Path, str]) -> str:
        """
        Read entire text file content.

        WHAT: Reads entire text file content as string with UTF-8 encoding.
        WHY: Provides consistent interface for text file reading across all modules.

        Args:
            file_path: Path to text file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is not UTF-8
            PermissionError: If file can't be read

        Example:
            >>> content = FileManager.read_text("README.md")
            >>> print(content[:50])
        """
        # Ensure Path object
        path = Path(file_path)

        # Guard clause: Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")

        # Guard clause: Check is file
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        # Read text content
        with open(path, 'r', encoding=FileManager.DEFAULT_ENCODING) as f:
            return f.read()

    @staticmethod
    def write_text(file_path: Union[Path, str], content: str) -> None:
        """
        Write string content to text file.

        WHAT: Writes string content to file with UTF-8 encoding, overwriting if exists.
        WHY: Provides consistent interface for text file writing across all modules.

        Args:
            file_path: Path to text file
            content: String content to write

        Raises:
            PermissionError: If file can't be written
            OSError: If disk is full or other I/O error

        Example:
            >>> FileManager.write_text("output.txt", "Hello, World!")
        """
        # Ensure Path object
        path = Path(file_path)

        # Ensure parent directory exists
        FileManager.ensure_directory(path.parent)

        # Write text content
        with open(path, 'w', encoding=FileManager.DEFAULT_ENCODING) as f:
            f.write(content)

    @staticmethod
    def read_lines(file_path: Union[Path, str]) -> List[str]:
        """
        Read text file as list of lines.

        WHAT: Reads text file and returns list of lines (with newlines stripped).
        WHY: Common pattern for processing line-based files (logs, CSV, etc).

        Args:
            file_path: Path to text file

        Returns:
            List of lines (newlines stripped)

        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file encoding is not UTF-8

        Example:
            >>> lines = FileManager.read_lines("data.txt")
            >>> for line in lines:
            ...     print(line)
        """
        # Ensure Path object
        path = Path(file_path)

        # Guard clause: Check file exists
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")

        # Read and return lines (stripped)
        with open(path, 'r', encoding=FileManager.DEFAULT_ENCODING) as f:
            return [line.rstrip('\n\r') for line in f]

    @staticmethod
    def write_lines(file_path: Union[Path, str], lines: List[str]) -> None:
        """
        Write list of lines to text file.

        WHAT: Writes list of strings to file, adding newlines between lines.
        WHY: Common pattern for writing line-based files (logs, reports, etc).

        Args:
            file_path: Path to text file
            lines: List of lines to write

        Raises:
            PermissionError: If file can't be written
            OSError: If disk is full or other I/O error

        Example:
            >>> lines = ["Line 1", "Line 2", "Line 3"]
            >>> FileManager.write_lines("output.txt", lines)
        """
        # Ensure Path object
        path = Path(file_path)

        # Ensure parent directory exists
        FileManager.ensure_directory(path.parent)

        # Write lines with newlines
        with open(path, 'w', encoding=FileManager.DEFAULT_ENCODING) as f:
            f.write('\n'.join(lines))
            if lines:  # Add trailing newline if non-empty
                f.write('\n')

    @staticmethod
    def append_text(file_path: Union[Path, str], content: str) -> None:
        """
        Append string content to text file.

        WHAT: Appends string to file, creating file if it doesn't exist.
        WHY: Common pattern for logging and incremental file building.

        Args:
            file_path: Path to text file
            content: String content to append

        Raises:
            PermissionError: If file can't be written
            OSError: If disk is full or other I/O error

        Example:
            >>> FileManager.append_text("log.txt", "New log entry\\n")
        """
        # Ensure Path object
        path = Path(file_path)

        # Ensure parent directory exists
        FileManager.ensure_directory(path.parent)

        # Append content
        with open(path, 'a', encoding=FileManager.DEFAULT_ENCODING) as f:
            f.write(content)

    @staticmethod
    def ensure_directory(dir_path: Union[Path, str]) -> None:
        """
        Ensure directory exists, creating it if necessary.

        WHAT: Creates directory and all parent directories if they don't exist.
        WHY: Prevents FileNotFoundError when writing files to new directories.
             Idempotent - safe to call multiple times.

        Args:
            dir_path: Path to directory

        Raises:
            PermissionError: If directory can't be created
            FileExistsError: If path exists but is not a directory

        Example:
            >>> FileManager.ensure_directory("output/reports/2024")
            >>> FileManager.write_text("output/reports/2024/report.txt", "data")
        """
        # Ensure Path object
        path = Path(dir_path)

        # Guard clause: Skip if already exists and is directory
        if path.exists() and path.is_dir():
            return

        # Guard clause: Fail if exists but is not directory
        if path.exists() and not path.is_dir():
            raise FileExistsError(f"Path exists but is not a directory: {path}")

        # Create directory with parents
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def file_exists(file_path: Union[Path, str]) -> bool:
        """
        Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            True if path exists and is a file

        WHY: Provides consistent interface for existence checks.

        Example:
            >>> if FileManager.file_exists("config.json"):
            ...     config = FileManager.read_json("config.json")
        """
        path = Path(file_path)
        return path.exists() and path.is_file()

    @staticmethod
    def directory_exists(dir_path: Union[Path, str]) -> bool:
        """
        Check if directory exists.

        Args:
            dir_path: Path to check

        Returns:
            True if path exists and is a directory

        WHY: Provides consistent interface for existence checks.

        Example:
            >>> if not FileManager.directory_exists("output"):
            ...     FileManager.ensure_directory("output")
        """
        path = Path(dir_path)
        return path.exists() and path.is_dir()

    @staticmethod
    def delete_file(file_path: Union[Path, str]) -> None:
        """
        Delete file if it exists.

        Args:
            file_path: Path to file to delete

        Raises:
            PermissionError: If file can't be deleted
            IsADirectoryError: If path is a directory

        WHY: Provides consistent interface for file deletion.

        Example:
            >>> FileManager.delete_file("temp.txt")
        """
        path = Path(file_path)

        # Guard clause: Skip if doesn't exist
        if not path.exists():
            return

        # Guard clause: Fail if is directory
        if path.is_dir():
            raise IsADirectoryError(f"Cannot delete directory with delete_file: {path}")

        # Delete file
        path.unlink()

    @staticmethod
    def get_file_size(file_path: Union[Path, str]) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist

        Example:
            >>> size = FileManager.get_file_size("data.json")
            >>> print(f"File size: {size} bytes")
        """
        path = Path(file_path)

        # Guard clause: Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return path.stat().st_size


# Service factory function for dependency injection
def create_file_manager() -> FileManager:
    """
    Factory function to create FileManager instance.

    WHY: Maintains consistency with other service modules, even though
         FileManager uses only static methods.
    PATTERN: Factory Method pattern

    Returns:
        FileManager instance (or class, since all methods are static)

    Example:
        >>> fm = create_file_manager()
        >>> fm.write_text("output.txt", "Hello!")
    """
    return FileManager()


__all__ = ["FileManager", "create_file_manager"]
