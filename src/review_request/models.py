#!/usr/bin/env python3
"""
WHY: Define immutable value objects for code review data structures
RESPONSIBILITY: Provide ImplementationFile value object with validation and serialization
PATTERNS: Value Object (immutable), Factory Method (from_dict, from_file_path)

The ImplementationFile value object ensures data integrity through:
- Immutability (frozen dataclass)
- Validation at construction
- Type safety
- Language inference from file extension
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from pathlib import Path


@dataclass(frozen=True)
class ImplementationFile:
    """
    Value Object: Represents a single implementation file

    Benefits:
    - Immutable (thread-safe)
    - Type-safe
    - Self-documenting
    - Validation at construction
    - Language auto-detection
    """
    path: str
    content: str
    lines: int
    language: str = field(default="")

    def __post_init__(self):
        """Validate file data and infer language if not set"""
        # Guard clause - validate path
        if not self.path:
            raise ValueError("File path cannot be empty")

        # Guard clause - validate lines
        if self.lines < 0:
            raise ValueError(f"Line count must be non-negative, got {self.lines}")

        # If language is not set, infer from file extension
        if not self.language:
            from review_request.language_detector import LanguageDetector
            detector = LanguageDetector()
            inferred_language = detector.detect_from_path(self.path)
            object.__setattr__(self, 'language', inferred_language)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization

        Returns:
            Dictionary representation of the file
        """
        return {
            'path': self.path,
            'content': self.content,
            'lines': self.lines,
            'language': self.language
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImplementationFile':
        """
        Create ImplementationFile from dictionary

        Args:
            data: Dictionary containing file data

        Returns:
            ImplementationFile instance
        """
        return cls(
            path=data['path'],
            content=data['content'],
            lines=data['lines'],
            language=data.get('language', '')
        )

    @classmethod
    def from_file_path(cls, file_path: Path, base_path: Path) -> 'ImplementationFile':
        """
        Create ImplementationFile from file path

        Args:
            file_path: Path to the file
            base_path: Base path for relative path calculation

        Returns:
            ImplementationFile instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        relative_path = file_path.relative_to(base_path)
        line_count = len(content.split('\n'))

        return cls(
            path=str(relative_path),
            content=content,
            lines=line_count
        )

    def format_for_review(self) -> str:
        """
        Format file content for code review display

        Returns:
            Markdown-formatted file content
        """
        return f"""## File: {self.path}
```
{self.content}
```
"""
