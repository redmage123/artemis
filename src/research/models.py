#!/usr/bin/env python3
"""
Research Models

WHY: Defines the data structures used throughout the research system to represent
research examples and results in a type-safe, immutable way.

RESPONSIBILITY: Provides dataclasses for research domain objects:
- ResearchExample: Represents a code example found during research
- Encapsulates all metadata about a research finding (title, content, source, etc.)

PATTERNS:
- Dataclass Pattern: Immutable data structures with automatic __init__, __repr__
- Value Object Pattern: Represents domain concepts as immutable values
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ResearchExample:
    """
    Represents a code example found during research.

    This is a value object that encapsulates all information about a research finding,
    including its source, content, and relevance score.

    Attributes:
        title: Human-readable title of the example
        content: The actual code or text content
        source: Name of the research source (GitHub, HuggingFace, Local)
        url: Optional URL to the original source
        language: Programming language or format of the content
        tags: List of tags/keywords for categorization
        relevance_score: Floating point relevance score (0.0 to 1.0+)
    """
    title: str
    content: str
    source: str
    url: Optional[str]
    language: str
    tags: List[str]
    relevance_score: float

    def __post_init__(self) -> None:
        """Validate fields after initialization"""
        if not self.title:
            raise ValueError("ResearchExample title cannot be empty")
        if not self.source:
            raise ValueError("ResearchExample source cannot be empty")
        if self.relevance_score < 0:
            raise ValueError("ResearchExample relevance_score cannot be negative")
