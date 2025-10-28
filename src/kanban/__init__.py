#!/usr/bin/env python3
"""
Package: kanban

WHY: Modularizes Kanban board management into focused, maintainable components
     that separate card creation, board operations, and CLI interface concerns.

RESPONSIBILITY:
- Export all public classes and functions from the kanban package
- Provide clean API for Kanban board operations
- Enable backward compatibility via re-exports

PATTERNS:
- Facade Pattern: Provides simplified interface to kanban subsystem
- Package Organization: Groups related functionality into cohesive modules

MODULES:
- card_builder: Builder pattern for card creation with validation
- board: Core Kanban board operations and state management
- cli: Command-line interface for manual board operations

PUBLIC API:
    from kanban import CardBuilder, KanbanBoard, BOARD_PATH

    # Create and add card using builder
    board = KanbanBoard()
    card = (board.new_card("TASK-001", "Feature")
        .with_priority("high")
        .with_story_points(8)
        .build())
    board.add_card(card)
"""

from kanban.card_builder import CardBuilder
from kanban.board import KanbanBoard, BOARD_PATH

__all__ = [
    'CardBuilder',
    'KanbanBoard',
    'BOARD_PATH',
]
