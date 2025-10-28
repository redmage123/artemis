#!/usr/bin/env python3
"""
RAG Storage Operations

WHY: Store architecture artifacts in RAG database
RESPONSIBILITY: Manage RAG operations for architecture stage
PATTERNS: Single Responsibility, Guard Clauses
"""

import json
from datetime import datetime
from typing import Optional, Any, List, Dict

from rag_storage_helper import RAGStorageHelper


class RAGArchitectureStorage:
    """
    Stores architecture artifacts in RAG database.

    WHY: Separate RAG operations from main stage logic
    RESPONSIBILITY: RAG storage operations only
    PATTERNS: Single Responsibility, Guard Clauses
    """

    def __init__(self, rag: Any, logger: Optional[Any] = None):
        """
        Initialize RAG storage.

        Args:
            rag: RAG agent instance
            logger: Logger interface
        """
        self.rag = rag
        self.logger = logger

    def store_adr(
        self,
        card_id: str,
        task_title: str,
        adr_content: str,
        adr_number: str,
        adr_path: str,
        card: Dict
    ) -> bool:
        """
        Store ADR in RAG database.

        Args:
            card_id: Card ID
            task_title: Task title
            adr_content: ADR content
            adr_number: ADR number
            adr_path: Path to ADR file
            card: Task card with metadata

        Returns:
            True if stored successfully, False otherwise

        WHY: Central entry point for ADR storage
        PATTERN: Guard clause for errors
        """
        try:
            RAGStorageHelper.store_stage_artifact(
                rag=self.rag,
                stage_name="architecture_decision",
                card_id=card_id,
                task_title=task_title,
                content=adr_content,
                metadata={
                    "adr_number": adr_number,
                    "priority": card.get('priority', 'medium'),
                    "story_points": card.get('points', 5),
                    "adr_file": adr_path
                }
            )
            return True

        except Exception as e:
            if self.logger:
                self.logger.log(f"⚠️  Failed to store ADR in RAG: {e}", "WARNING")
            return False

    def store_kanban_state(
        self,
        card_id: str,
        story_card_ids: List[str],
        board: Any
    ) -> bool:
        """
        Store Kanban board state in RAG database.

        Args:
            card_id: Parent card ID
            story_card_ids: List of generated story card IDs
            board: Kanban board instance

        Returns:
            True if stored successfully, False otherwise

        WHY: Track board state for traceability
        PATTERN: Guard clauses for errors
        """
        try:
            board_state = {
                "parent_card": card_id,
                "generated_stories": story_card_ids,
                "columns": {},
                "total_cards": 0
            }

            # Collect all cards by column
            if hasattr(board, 'columns'):
                self._collect_cards_by_column(board, board_state)

            RAGStorageHelper.store_stage_artifact(
                rag=self.rag,
                stage_name="kanban_board_state",
                card_id=card_id,
                task_title=f"Kanban State after ADR-{card_id}",
                content=json.dumps(board_state, indent=2),
                metadata={
                    "parent_card": card_id,
                    "story_count": len(story_card_ids),
                    "total_cards": board_state["total_cards"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            if self.logger:
                self.logger.log(
                    f"✅ Stored Kanban board state in RAG ({board_state['total_cards']} cards)",
                    "INFO"
                )

            return True

        except Exception as e:
            if self.logger:
                self.logger.log(f"⚠️  Failed to store Kanban in RAG: {e}", "WARNING")
            return False

    def _collect_cards_by_column(self, board: Any, board_state: Dict) -> None:
        """
        Collect all cards by column and update board state.

        WHY: Helper to gather board state
        PATTERN: Guard clause for column iteration
        """
        for column_name in board.columns:
            cards = board.get_cards_in_column(column_name)
            board_state["columns"][column_name] = [
                {
                    "card_id": c.get('card_id'),
                    "title": c.get('title'),
                    "priority": c.get('priority'),
                    "points": c.get('points')
                }
                for c in cards
            ]
            board_state["total_cards"] += len(cards)
