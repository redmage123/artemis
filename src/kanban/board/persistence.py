#!/usr/bin/env python3
"""
Module: kanban/board/persistence.py

WHY: Separates board persistence logic from business operations
     Handles file I/O and backward compatibility

RESPONSIBILITY:
- Load board state from JSON file
- Save board state to JSON file
- Ensure metrics field exists (backward compatibility)
- Timestamp management

PATTERNS:
- Repository Pattern: Encapsulates data access
- Guard Clauses: Early validation returns
"""

import json
import os
from datetime import datetime
from typing import Dict

from artemis_exceptions import (
    KanbanBoardError,
    FileReadError,
    wrap_exception
)


class BoardPersistence:
    """
    Board persistence operations for JSON backend.

    WHY: Separates persistence concerns from business logic
    RESPONSIBILITY: Load and save board state
    PATTERNS: Repository pattern
    """

    DEFAULT_METRICS = {
        'cycle_time_avg_hours': 0,
        'cycle_time_min_hours': 0,
        'cycle_time_max_hours': 0,
        'cards_completed': 0,
        'throughput_current_sprint': 0,
        'velocity_current_sprint': 0,
        'wip_violations_count': 0,
        'blocked_items_count': 0
    }

    @staticmethod
    def load_board(board_path: str) -> Dict:
        """
        Load board state from JSON file with backward compatibility.

        WHY: Reads persisted board state, ensuring metrics field exists
        PERFORMANCE: Single file read operation

        Args:
            board_path: Path to kanban_board.json file

        Returns:
            Board dictionary with columns, metrics, sprints

        Raises:
            KanbanBoardError: If file not found
            FileReadError: If JSON parsing fails
        """
        # Guard clause: file existence
        if not os.path.exists(board_path):
            raise KanbanBoardError(
                f"Kanban board not found at {board_path}",
                context={"board_path": board_path}
            )

        try:
            with open(board_path, 'r') as f:
                board = json.load(f)

                # Ensure metrics field exists (backward compatibility)
                if 'metrics' not in board:
                    board['metrics'] = BoardPersistence.DEFAULT_METRICS.copy()

                return board

        except Exception as e:
            raise wrap_exception(
                e,
                FileReadError,
                "Failed to read Kanban board",
                context={"board_path": board_path}
            )

    @staticmethod
    def save_board(board: Dict, board_path: str) -> None:
        """
        Save board to JSON file with timestamp.

        WHY: Persists board state with audit trail
        PERFORMANCE: Single file write operation

        Args:
            board: Board dictionary to save
            board_path: Path to kanban_board.json file

        Raises:
            FileWriteError: If write fails
        """
        board['last_updated'] = datetime.utcnow().isoformat() + 'Z'

        try:
            with open(board_path, 'w') as f:
                json.dump(board, f, indent=2)
        except Exception as e:
            raise wrap_exception(
                e,
                FileReadError,
                "Failed to save Kanban board",
                context={"board_path": board_path}
            )
