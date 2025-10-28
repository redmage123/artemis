#!/usr/bin/env python3
"""
Package: kanban.board

WHY: Modular Kanban board implementation following Single Responsibility Principle
     Each module has one clear purpose, improving maintainability and testability

RESPONSIBILITY:
- Provide clean public API for board operations
- Export main KanbanBoard facade
- Hide internal implementation details

PATTERNS:
- Facade Pattern: KanbanBoard provides unified interface
- Package Organization: Related functionality grouped together

Module Structure:
- models.py: Data structure access and queries
- persistence.py: JSON load/save operations
- card_operations.py: Card CRUD and workflow
- sprint_manager.py: Sprint lifecycle management
- metrics_calculator.py: Performance metrics
- board_visualizer.py: Console output formatting
- board_facade.py: Main orchestrator (KanbanBoard class)

Public API:
- KanbanBoard: Main class for all board operations
"""

from kanban.board.board_facade import KanbanBoard

__all__ = ['KanbanBoard']
