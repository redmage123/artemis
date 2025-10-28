#!/usr/bin/env python3
"""
Module: kanban_manager.py (BACKWARD COMPATIBILITY WRAPPER)

PURPOSE: Maintains backward compatibility for existing imports while redirecting
         to the new modularized kanban package structure.

DEPRECATION NOTICE:
    This file is a compatibility wrapper. New code should import from the kanban package:

    OLD (still works):
        from kanban_manager import KanbanBoard, CardBuilder

    NEW (preferred):
        from kanban import KanbanBoard, CardBuilder
        from kanban.board import KanbanBoard
        from kanban.card_builder import CardBuilder

MIGRATION PATH:
    1. All functionality moved to kanban/ package
    2. This wrapper re-exports for backward compatibility
    3. Eventually this file can be removed after migration

STRUCTURE:
    kanban/
    ├── __init__.py          - Package exports
    ├── card_builder.py      - CardBuilder class (Builder pattern for cards)
    ├── board.py             - KanbanBoard class (board operations & persistence)
    └── cli.py               - CLI interface (main() function)

WHY REFACTORED:
    - Original file was 1,284 lines (violates SRP)
    - Mixed card creation, board management, and CLI concerns
    - Hard to test and maintain individual components
    - New structure separates concerns into focused modules
"""

# Re-export all public classes and constants for backward compatibility
from kanban.card_builder import CardBuilder
from kanban.board import KanbanBoard, BOARD_PATH
from kanban.cli import main

# Preserve module-level constants
__all__ = [
    'CardBuilder',
    'KanbanBoard',
    'BOARD_PATH',
    'main',
]

# Preserve CLI entry point for existing scripts
if __name__ == "__main__":
    main()
