#!/usr/bin/env python3
"""
User Story Models - Data structures for user stories

WHY: Define clear data structures for user story representation.
RESPONSIBILITY: Data models and type definitions only.
PATTERNS: Data classes, immutability, type safety.

Example:
    story = UserStory(
        title="As a user...",
        description="Details",
        acceptance_criteria=["Given..."],
        points=5,
        priority="high"
    )
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


# Constants for validation (DRY: single source of truth)
VALID_PRIORITIES = ['low', 'medium', 'high', 'critical']
MIN_STORY_POINTS = 1
MAX_STORY_POINTS = 8
REQUIRED_STORY_FIELDS = ['title', 'description', 'acceptance_criteria', 'points', 'priority']


@dataclass(frozen=True)
class UserStory:
    """
    Immutable user story data structure.

    WHY: Immutability prevents bugs from unexpected mutations.
    PATTERNS: Data class for clean data modeling, frozen for immutability.

    Attributes:
        title: Story title in "As a X, I want Y, so that Z" format
        description: Detailed description of implementation
        acceptance_criteria: List of acceptance criteria
        points: Story points (1-8 scale)
        priority: Priority level (low, medium, high, critical)
    """
    title: str
    description: str
    acceptance_criteria: List[str]
    points: int
    priority: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.

        WHY: Support JSON serialization and backward compatibility.
        PERFORMANCE: O(1) - simple attribute access.

        Returns:
            Dictionary with story fields
        """
        return {
            'title': self.title,
            'description': self.description,
            'acceptance_criteria': self.acceptance_criteria,
            'points': self.points,
            'priority': self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStory':
        """
        Create UserStory from dictionary.

        WHY: Support deserialization from JSON/dict sources.
        PATTERN: Factory method for object creation.

        Args:
            data: Dictionary with story fields

        Returns:
            UserStory instance

        Raises:
            ValueError: If required fields are missing
        """
        # Guard clause: validate required fields
        missing_fields = [f for f in REQUIRED_STORY_FIELDS if f not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        return cls(
            title=data['title'],
            description=data['description'],
            acceptance_criteria=data['acceptance_criteria'],
            points=data['points'],
            priority=data['priority']
        )


@dataclass(frozen=True)
class PromptContext:
    """
    Context for user story generation prompts.

    WHY: Encapsulate prompt generation context in a single structure.
    PATTERNS: Data class, immutability.

    Attributes:
        adr_content: ADR content to convert
        adr_number: ADR number (e.g., "001")
        context: Generation context description
        constraints: Generation constraints
        scale_expectations: Expected number of stories
    """
    adr_content: str
    adr_number: str
    context: str = "Converting ADR to user stories"
    constraints: str = "Focus on implementation tasks"
    scale_expectations: str = "2-5 user stories"

    def get_variables_dict(self) -> Dict[str, str]:
        """
        Get variables as dictionary for prompt rendering.

        WHY: Support prompt template variable substitution.
        PERFORMANCE: O(1) - simple attribute access.

        Returns:
            Dictionary of prompt variables
        """
        return {
            'context': self.context,
            'requirements': self.adr_content,
            'constraints': self.constraints,
            'scale_expectations': self.scale_expectations
        }


@dataclass(frozen=True)
class GenerationConfig:
    """
    Configuration for user story generation.

    WHY: Encapsulate LLM generation parameters.
    PATTERNS: Data class, immutability, defaults.

    Attributes:
        temperature: LLM temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        min_stories: Minimum expected stories
        max_stories: Maximum expected stories
    """
    temperature: float = 0.4
    max_tokens: int = 2000
    min_stories: int = 2
    max_stories: int = 5

    def validate(self) -> bool:
        """
        Validate configuration values.

        WHY: Prevent invalid LLM parameters.
        PERFORMANCE: O(1) - simple comparisons.

        Returns:
            True if valid, False otherwise
        """
        # Guard clauses for validation
        if not 0.0 <= self.temperature <= 1.0:
            return False
        if self.max_tokens <= 0:
            return False
        if self.min_stories < 0 or self.max_stories < self.min_stories:
            return False
        return True
