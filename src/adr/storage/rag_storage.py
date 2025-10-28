#!/usr/bin/env python3
"""
WHY: Handle ADR storage in RAG database
RESPONSIBILITY: Store ADR content and Kanban state in RAG
PATTERNS: Strategy (storage implementation), Guard Clause (error handling)

RAG storage provides durable artifact persistence with semantic search.
"""

import json
from datetime import datetime
from typing import List
from artemis_stage_interface import LoggerInterface


class ADRRagStorage:
    """
    Handles ADR storage in RAG database.

    WHY: Separates RAG storage logic from service orchestration.
    RESPONSIBILITY: Store ADR artifacts and Kanban snapshots in RAG.
    PATTERNS: Strategy, Guard Clause.
    """

    def __init__(self, rag, logger: LoggerInterface):
        """
        Initialize RAG storage.

        Args:
            rag: RAG agent for artifact storage
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
        priority: str = "medium",
        story_points: int = 5
    ) -> None:
        """
        Store ADR content in RAG database.

        WHY: Enables semantic search and retrieval of ADRs.

        Args:
            card_id: Card ID for this task
            task_title: Task title
            adr_content: Full ADR content
            adr_number: ADR number (e.g., "001")
            adr_path: Path to ADR file
            priority: Task priority
            story_points: Story points
        """
        try:
            self.rag.store_artifact(
                artifact_type="architecture_decision",
                card_id=card_id,
                task_title=task_title,
                content=adr_content,
                metadata={
                    "adr_number": adr_number,
                    "priority": priority,
                    "story_points": story_points,
                    "adr_file": adr_path
                }
            )
            self.logger.log(
                f"✅ Stored ADR-{adr_number} in RAG database",
                "INFO"
            )
        except Exception as e:
            self.logger.log(
                f"⚠️  Failed to store ADR in RAG: {e}",
                "WARNING"
            )

    def store_kanban_state(
        self,
        card_id: str,
        story_card_ids: List[str],
        board
    ) -> None:
        """
        Store Kanban board state in RAG database.

        WHY: Creates snapshot for tracking project evolution.

        Args:
            card_id: Parent card ID
            story_card_ids: List of generated story card IDs
            board: Kanban board instance
        """
        try:
            # Build board state snapshot
            board_state = {
                "parent_card": card_id,
                "generated_stories": story_card_ids,
                "columns": {},
                "total_cards": 0
            }

            # Collect all cards by column
            if hasattr(board, 'columns'):
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

            # Store in RAG
            self.rag.store_artifact(
                artifact_type="kanban_board_state",
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

            self.logger.log(
                f"✅ Stored Kanban board state in RAG "
                f"({board_state['total_cards']} cards)",
                "INFO"
            )

        except Exception as e:
            self.logger.log(
                f"⚠️  Failed to store Kanban in RAG: {e}",
                "WARNING"
            )
