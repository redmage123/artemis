#!/usr/bin/env python3
"""
Module: kanban/board.py (BACKWARD COMPATIBILITY WRAPPER)

WHY: Maintains 100% backward compatibility with existing imports
     All existing code using 'from kanban.board import KanbanBoard' continues to work

RESPONSIBILITY:
- Re-export KanbanBoard from new package structure
- Maintain backward compatibility
- Redirect to modular implementation

PATTERNS:
- Facade Pattern: Transparent redirection to new implementation
- Backward Compatibility: No breaking changes

MIGRATION NOTE:
This file now imports from kanban.board package. The original 977-line implementation
has been refactored into a modular package structure at kanban/board/:

New Package Structure:
- kanban/board/models.py (234 lines): Data structure access
- kanban/board/persistence.py (108 lines): JSON load/save
- kanban/board/card_operations.py (296 lines): Card CRUD operations
- kanban/board/sprint_manager.py (287 lines): Sprint management
- kanban/board/metrics_calculator.py (118 lines): Metrics calculation
- kanban/board/board_visualizer.py (131 lines): Console visualization
- kanban/board/board_facade.py (513 lines): Main orchestrator
- kanban/board/__init__.py (34 lines): Public API

Total modular code: ~1,721 lines (includes documentation following claude.md standards)
Original file: 977 lines
This wrapper: ~40 lines

Benefits of Refactoring:
1. Single Responsibility: Each module has one clear purpose
2. Testability: Small, focused modules are easier to test
3. Maintainability: Changes isolated to specific modules
4. Readability: Clear separation of concerns
5. Reusability: Modules can be used independently
6. Type Safety: Complete type hints throughout
7. Performance: No nested loops, uses comprehensions and generators
8. Documentation: WHY/RESPONSIBILITY/PATTERNS headers on all modules

Original file preserved at: kanban/board_original.py
"""

# Re-export KanbanBoard from new package (100% backward compatible)
from kanban.board import KanbanBoard

# Re-export BOARD_PATH constant for backward compatibility
from artemis_constants import KANBAN_BOARD_PATH
BOARD_PATH = str(KANBAN_BOARD_PATH)

# Public API (identical to original)
__all__ = ['KanbanBoard', 'BOARD_PATH']
