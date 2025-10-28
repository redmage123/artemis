#!/usr/bin/env python3
"""
Configuration Path Utilities

WHY: Handles path resolution and validation logic

RESPONSIBILITY: Provide utilities for resolving and validating file paths

PATTERNS: Pure functions for path operations
"""

import os
from pathlib import Path
from typing import Optional


def resolve_relative_path(path: str, script_dir: Optional[str] = None) -> str:
    """
    Resolve relative path to absolute path

    WHY: Centralizes path resolution logic to avoid duplication

    Args:
        path: Path to resolve (may be absolute or relative)
        script_dir: Script directory to use as base (defaults to src directory)

    Returns:
        Absolute path
    """
    # Guard clause: Already absolute
    if os.path.isabs(path):
        return path

    # Use provided script_dir or calculate from parent directory (src/)
    if not script_dir:
        # Go up one level from config/ to src/
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(script_dir, path)


def ensure_directory_writable(path: Path) -> tuple[bool, Optional[str]]:
    """
    Ensure directory exists and is writable

    WHY: Centralizes directory validation logic

    Args:
        path: Path to check

    Returns:
        Tuple of (success, error_message)
    """
    try:
        path.mkdir(parents=True, exist_ok=True)

        # Check writable
        test_file = path / ".test_write"
        test_file.write_text("test")
        test_file.unlink()

        return True, None
    except Exception as e:
        return False, str(e)


def get_script_directory() -> str:
    """
    Get the directory containing the current script

    WHY: Centralizes script directory resolution

    Returns:
        Absolute path to src directory
    """
    # Go up one level from config/ to src/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
