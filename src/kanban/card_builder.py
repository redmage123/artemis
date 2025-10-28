#!/usr/bin/env python3
"""
Module: kanban/card_builder.py

WHY: Eliminates "parameter overload" anti-pattern where card creation required 9+ parameters,
     making code hard to read and maintain. Provides fluent, readable API for card creation.

RESPONSIBILITY:
- Enforce required fields (task_id, title) for card creation
- Provide sensible defaults for optional fields
- Validate field values (priority, size, story points)
- Auto-normalize story points to Fibonacci scale
- Generate unique card_id and timestamps on build()

PATTERNS:
- Builder Pattern: Fluent API makes card creation self-documenting and easy to modify
- Fail-fast validation: Validates at build-time to provide clear error messages

USAGE:
    card = (CardBuilder("TASK-001", "Add feature")
        .with_description("Implement new API endpoint")
        .with_priority("high")
        .with_labels(["feature", "backend"])
        .with_story_points(8)
        .with_assigned_agents(["developer-a"])
        .build())
"""

from datetime import datetime
from typing import Dict, List


class CardBuilder:
    """
    Builder pattern for creating Kanban cards with sensible defaults

    Why it exists: Eliminates "parameter overload" anti-pattern where card creation
                   required 9+ parameters, making code hard to read and maintain.

    Design pattern: Builder Pattern
    Why this design: Provides fluent, readable API for card creation while ensuring
                     all required fields are set and optional fields have sensible defaults.

    Responsibilities:
    - Enforce required fields (task_id, title)
    - Provide sensible defaults for optional fields
    - Validate field values (priority, size, story points)
    - Auto-normalize story points to Fibonacci scale
    - Generate unique card_id and timestamps on build()

    Usage Example:
        card = (CardBuilder("TASK-001", "Add feature")
            .with_description("Implement new API endpoint")
            .with_priority("high")
            .with_labels(["feature", "backend"])
            .with_story_points(8)
            .with_assigned_agents(["developer-a"])
            .build())

    Why fluent API: Method chaining makes card creation self-documenting and easy to modify.
    """

    def __init__(self, task_id: str, title: str):
        """
        Initialize builder with only required fields

        Why minimal constructor: Reduces cognitive load - developers only need to remember
                                2 required fields instead of 9+.

        Args:
            task_id: Unique task identifier (e.g., "TASK-001" or "card-123")
            title: Human-readable card title

        Note: All other fields have sensible defaults and can be set via with_* methods
        """
        self._card = {
            'task_id': task_id,
            'title': title,
            'description': '',
            # Sensible defaults
            'priority': 'medium',
            'labels': [],
            'size': 'medium',
            'story_points': 3,
            'assigned_agents': [],
            'acceptance_criteria': [],
            'blocked': False,
            'blocked_reason': None,
        }

    def with_description(self, description: str) -> 'CardBuilder':
        """Set card description"""
        self._card['description'] = description
        return self

    def with_priority(self, priority: str) -> 'CardBuilder':
        """
        Set card priority level with validation

        Why needed: Ensures consistent priority values across the board, preventing
                    typos like "urgent" or "normal" which would break filtering.

        Args:
            priority: Must be 'high', 'medium', or 'low' (validated)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If priority is not one of the valid values

        Design note: Validation happens at build-time, not runtime, to fail fast
                     and provide clear error messages during card creation.
        """
        valid_priorities = ['high', 'medium', 'low']
        if priority not in valid_priorities:
            raise ValueError(
                f"Invalid priority: {priority}. Must be one of {valid_priorities}"
            )
        self._card['priority'] = priority
        return self

    def with_labels(self, labels: List[str]) -> 'CardBuilder':
        """Set card labels/tags"""
        self._card['labels'] = labels
        return self

    def with_size(self, size: str) -> 'CardBuilder':
        """
        Set card size

        Args:
            size: Must be 'small', 'medium', or 'large'

        Raises:
            ValueError: If size is invalid
        """
        valid_sizes = ['small', 'medium', 'large']
        if size not in valid_sizes:
            raise ValueError(
                f"Invalid size: {size}. Must be one of {valid_sizes}"
            )
        self._card['size'] = size
        return self

    def with_story_points(self, points: int) -> 'CardBuilder':
        """
        Set story points using Fibonacci scale

        Why Fibonacci scale: Research shows Fibonacci numbers provide better estimation
                            granularity for software tasks than linear scales. The increasing
                            gaps reflect growing uncertainty with larger tasks.

        Why auto-rounding: Allows callers to use any integer (e.g., from LLM estimation)
                          and automatically normalizes to valid Fibonacci value.

        Args:
            points: Desired story points (will be rounded to nearest Fibonacci)
                   Valid values: [1, 2, 3, 5, 8, 13]

        Returns:
            Self for method chaining

        Behavior:
            - 4 rounds to 3 or 5 (whichever is closer)
            - 7 rounds to 8
            - 15 rounds to 13
            - Values outside range use nearest boundary

        Note: Non-Fibonacci values are automatically rounded, not rejected, to be
              forgiving to LLM-generated values while maintaining scale consistency.
        """
        valid_points = [1, 2, 3, 5, 8, 13]
        if points not in valid_points:
            # Round to nearest Fibonacci value
            nearest = min(valid_points, key=lambda x: abs(x - points))
            self._card['story_points'] = nearest
        else:
            self._card['story_points'] = points
        return self

    def with_assigned_agents(self, agents: List[str]) -> 'CardBuilder':
        """Set assigned agents"""
        self._card['assigned_agents'] = agents
        return self

    def with_acceptance_criteria(self, criteria: List[Dict]) -> 'CardBuilder':
        """Set acceptance criteria"""
        self._card['acceptance_criteria'] = criteria
        return self

    def with_requirements_file(self, requirements_file: str) -> 'CardBuilder':
        """
        Set requirements file path for requirements parsing

        Args:
            requirements_file: Path to requirements document (PDF, Word, Excel, text, etc.)

        Returns:
            CardBuilder instance for fluent API
        """
        self._card['requirements_file'] = requirements_file
        return self

    def blocked(self, reason: str) -> 'CardBuilder':
        """Mark card as blocked with reason"""
        self._card['blocked'] = True
        self._card['blocked_reason'] = reason
        return self

    def build(self) -> Dict:
        """
        Build and return the complete card dictionary with generated fields

        Why needed: Finalizes card creation by adding system-generated fields like
                    timestamps, card_id, and default tracking structures.

        What it does:
        - Generates unique card_id from timestamp
        - Sets created_at and updated_at timestamps
        - Initializes test_status tracking structure
        - Initializes definition_of_done checklist
        - Creates initial history entry for audit trail
        - Sets default column to 'backlog'

        Returns:
            Complete card dictionary ready to be added to board via add_card()

        Design note: Build() is the "commit" operation - card is immutable after this.
                     This ensures all validation and defaults are applied before card
                     enters the system.
        """
        # Generate unique card ID
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        card_id = f"card-{timestamp}"

        # Add system-generated fields
        self._card.update({
            'card_id': card_id,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'moved_to_current_column_at': datetime.utcnow().isoformat() + 'Z',
            'current_column': 'backlog',
            'test_status': {
                'unit_tests_written': False,
                'unit_tests_passing': False,
                'integration_tests_written': False,
                'integration_tests_passing': False,
                'test_coverage_percent': 0
            },
            'definition_of_done': {
                'code_complete': False,
                'tests_passing': False,
                'code_reviewed': False,
                'documentation_updated': False,
                'deployed_to_production': False
            },
            'history': [
                {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'action': 'created',
                    'column': 'backlog',
                    'agent': 'system',
                    'comment': 'Card created via CardBuilder'
                }
            ]
        })

        return self._card
