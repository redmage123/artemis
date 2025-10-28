#!/usr/bin/env python3
"""
Module: kanban_updater.py

WHY: Update Kanban board with sprint information
RESPONSIBILITY: Persist sprint plans to board metadata and create sprint cards
PATTERNS: Batch operations to avoid N+1 queries
"""

from typing import List, Any
from sprint_models import Sprint, Clock, SystemClock
from artemis_stage_interface import LoggerInterface


class KanbanUpdater:
    """
    WHY: Separate Kanban update logic from sprint planning business logic
    RESPONSIBILITY: Update board with sprint metadata and cards
    PATTERNS: Batch operations, graceful degradation (log errors, don't fail)
    """

    def __init__(self, board: Any, logger: LoggerInterface, clock: Clock = None):
        """
        WHY: Need board interface and logger for updates

        Args:
            board: KanbanBoard interface
            logger: Logger for error handling
            clock: Clock for timestamps (default SystemClock)
        """
        self.board = board
        self.logger = logger
        self.clock = clock or SystemClock()

    def update_board(self, card_id: str, sprints: List[Sprint]) -> None:
        """
        WHY: Persist sprint plan to Kanban for visibility
        RESPONSIBILITY: Update card metadata and create sprint cards
        PATTERNS: Guard clause, batch operations, graceful degradation

        Args:
            card_id: Parent card ID
            sprints: List of Sprint objects to store
        """
        # Guard: No sprints to update
        if not sprints:
            return

        try:
            self._update_card_metadata(card_id, sprints)
            self._create_sprint_cards(card_id, sprints)
            self.logger.log(
                f"Updated Kanban board with {len(sprints)} sprints",
                "INFO"
            )
        except Exception as e:
            # Log but don't fail - Kanban update is not critical
            self.logger.log(
                f"Error updating Kanban board: {e}",
                "ERROR"
            )

    def _update_card_metadata(self, card_id: str, sprints: List[Sprint]) -> None:
        """
        WHY: Store sprint summary in parent card for quick access
        RESPONSIBILITY: Update card with sprint metadata
        """
        self.board.update_card(
            card_id,
            {
                'sprints': [s.to_dict() for s in sprints],
                'sprint_planning_completed': True,
                'total_sprints': len(sprints),
                'planned_at': self.clock.now().isoformat()
            }
        )

    def _create_sprint_cards(self, card_id: str, sprints: List[Sprint]) -> None:
        """
        WHY: Create individual cards for each sprint for tracking
        RESPONSIBILITY: Build and batch-create sprint cards
        PATTERNS: Batch operations to avoid N+1 database queries
        """
        sprint_cards = [
            self._build_sprint_card(card_id, sprint)
            for sprint in sprints
        ]

        # Try batch operation first (more efficient)
        if hasattr(self.board, 'add_cards_batch'):
            self.board.add_cards_batch(sprint_cards)
        else:
            # Fallback to individual adds
            for sprint_card in sprint_cards:
                self.board.add_card(sprint_card)

    def _build_sprint_card(self, parent_card_id: str, sprint: Sprint) -> dict:
        """
        WHY: Consistent sprint card structure
        RESPONSIBILITY: Build sprint card dictionary
        """
        sprint_card_id = f"{parent_card_id}-sprint-{sprint.sprint_number}"
        return {
            'card_id': sprint_card_id,
            'title': f"Sprint {sprint.sprint_number}",
            'description': (
                f"{len(sprint.features)} features, "
                f"{sprint.total_story_points} points"
            ),
            'metadata': {
                'sprint_number': sprint.sprint_number,
                'features': [f.to_dict() for f in sprint.features],
                'start_date': sprint.start_date.strftime('%Y-%m-%d'),
                'end_date': sprint.end_date.strftime('%Y-%m-%d'),
                'parent_card_id': parent_card_id
            },
            'column': 'backlog'
        }
