#!/usr/bin/env python3
"""
Module: kanban/board/card_operations.py

WHY: Encapsulates all card-related operations (CRUD, movement, blocking)
     Enforces WIP limits and tracks card history

RESPONSIBILITY:
- Card CRUD operations (add, update, move)
- Card blocking/unblocking workflow
- Test status updates
- Acceptance criteria verification
- WIP limit enforcement

PATTERNS:
- Command Pattern: Each operation is self-contained
- Strategy Pattern: Dictionary mapping for status updates
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional

from artemis_exceptions import KanbanBoardError
from kanban.board.models import BoardModels


class CardOperations:
    """
    Card lifecycle operations with WIP enforcement.

    WHY: Centralizes card operations and business rules
    RESPONSIBILITY: Card CRUD and workflow management
    PATTERNS: Command pattern for operations
    """

    @staticmethod
    def add_card(board: Dict, card: Dict) -> Dict:
        """
        Add a pre-built card to the backlog.

        WHY: Creates new cards in the system
        PERFORMANCE: O(1) append operation

        Args:
            board: Board dictionary
            card: Card dictionary (from CardBuilder.build())

        Returns:
            Added card dictionary

        Raises:
            KanbanBoardError: If backlog column not found
        """
        backlog = BoardModels.get_column(board, "backlog")
        if not backlog:
            raise KanbanBoardError(
                "Backlog column not found",
                context={"board": board.get('board_id', 'unknown')}
            )

        backlog['cards'].append(card)
        return card

    @staticmethod
    def move_card(
        board: Dict,
        card_id: str,
        to_column: str,
        agent: str = "system",
        comment: str = ""
    ) -> bool:
        """
        Move a card between columns with WIP enforcement.

        WHY: Core workflow operation for card transitions
        PERFORMANCE: O(n) for card search, O(1) for move

        Args:
            board: Board dictionary
            card_id: Card identifier to move
            to_column: Destination column ID
            agent: Name of agent performing move
            comment: Optional comment

        Returns:
            True if move succeeded, False otherwise
        """
        card, from_column = BoardModels.find_card(board, card_id)

        # Guard clause: card not found
        if not card:
            return False

        to_col = BoardModels.get_column(board, to_column)

        # Guard clause: destination not found
        if not to_col:
            return False

        # Check WIP limit
        if to_col['wip_limit'] is not None:
            if len(to_col['cards']) >= to_col['wip_limit']:
                board['metrics']['wip_violations_count'] += 1

        # Remove from current column
        from_col = BoardModels.get_column(board, from_column)
        if from_col:
            from_col['cards'] = [
                c for c in from_col['cards']
                if c['card_id'] != card_id
            ]

        # Update card metadata
        card['current_column'] = to_column
        card['moved_to_current_column_at'] = datetime.utcnow().isoformat() + 'Z'

        # Add history entry
        card['history'].append({
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "action": "moved",
            "from_column": from_column,
            "to_column": to_column,
            "agent": agent,
            "comment": comment or f"Moved from {from_column} to {to_column}"
        })

        # Add to new column
        to_col['cards'].append(card)

        # Mark completion if moved to done
        if to_column == "done":
            CardOperations._mark_card_completed(card)

        return True

    @staticmethod
    def _mark_card_completed(card: Dict) -> None:
        """
        Mark card as completed and calculate cycle time.

        WHY: Separated for clarity and testability
        PERFORMANCE: O(1) time calculations
        """
        card['completed_at'] = datetime.utcnow().isoformat() + 'Z'

        # Calculate cycle time
        created = datetime.fromisoformat(card['created_at'].replace('Z', '+00:00'))
        completed = datetime.now(timezone.utc)
        cycle_time_hours = (completed - created).total_seconds() / 3600
        card['cycle_time_hours'] = round(cycle_time_hours, 2)

    @staticmethod
    def update_card(
        board: Dict,
        card_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update card fields.

        WHY: Allows partial card updates
        PERFORMANCE: O(n) for card search

        Args:
            board: Board dictionary
            card_id: Card to update
            updates: Dictionary of field updates

        Returns:
            True if successful
        """
        card, _ = BoardModels.find_card(board, card_id)

        # Guard clause: card not found
        if not card:
            return False

        # Update fields
        for key, value in updates.items():
            if key in card:
                card[key] = value

        return True

    @staticmethod
    def block_card(
        board: Dict,
        card_id: str,
        reason: str,
        agent: str = "system"
    ) -> bool:
        """
        Mark a card as blocked and move to Blocked column.

        WHY: Tracks blockers in workflow
        PERFORMANCE: O(n) for move operation

        Args:
            board: Board dictionary
            card_id: Card to block
            reason: Reason for blocking
            agent: Agent reporting the block

        Returns:
            True if successful
        """
        card, _ = BoardModels.find_card(board, card_id)

        # Guard clause: card not found
        if not card:
            return False

        card['blocked'] = True
        card['blocked_reason'] = reason

        # Move to blocked column
        CardOperations.move_card(
            board,
            card_id,
            "blocked",
            agent,
            f"BLOCKED: {reason}"
        )

        # Update metrics
        blocked_column = BoardModels.get_column(board, "blocked")
        if blocked_column:
            board['metrics']['blocked_items_count'] = len(blocked_column['cards'])

        return True

    @staticmethod
    def unblock_card(
        board: Dict,
        card_id: str,
        move_to_column: str,
        agent: str = "system",
        resolution: str = ""
    ) -> bool:
        """
        Unblock a card and move to specified column.

        WHY: Resolves blockers and resumes workflow
        PERFORMANCE: O(n) for move operation

        Args:
            board: Board dictionary
            card_id: Card to unblock
            move_to_column: Where to move the card
            agent: Agent unblocking
            resolution: How the block was resolved

        Returns:
            True if successful
        """
        card, column = BoardModels.find_card(board, card_id)

        # Guard clause: not in blocked column
        if not card or column != "blocked":
            return False

        card['blocked'] = False
        card['blocked_reason'] = None

        # Move to destination column
        CardOperations.move_card(
            board,
            card_id,
            move_to_column,
            agent,
            f"UNBLOCKED: {resolution}"
        )

        # Update metrics
        blocked_column = BoardModels.get_column(board, "blocked")
        if blocked_column:
            board['metrics']['blocked_items_count'] = len(blocked_column['cards'])

        return True

    @staticmethod
    def update_test_status(
        board: Dict,
        card_id: str,
        test_status: Dict[str, Any]
    ) -> bool:
        """
        Update test status for a card.

        WHY: Tracks testing progress
        PERFORMANCE: O(n) for card search

        Args:
            board: Board dictionary
            card_id: Card to update
            test_status: Dictionary with test status fields

        Returns:
            True if successful
        """
        card, _ = BoardModels.find_card(board, card_id)

        # Guard clause: card not found
        if not card:
            return False

        card['test_status'].update(test_status)
        return True

    @staticmethod
    def verify_acceptance_criterion(
        board: Dict,
        card_id: str,
        criterion_index: int,
        verified_by: str
    ) -> bool:
        """
        Mark an acceptance criterion as verified.

        WHY: Tracks acceptance criteria completion
        PERFORMANCE: O(n) for card search

        Args:
            board: Board dictionary
            card_id: Card ID
            criterion_index: Index of criterion to verify
            verified_by: Agent verifying

        Returns:
            True if successful
        """
        card, _ = BoardModels.find_card(board, card_id)

        # Guard clause: card not found
        if not card:
            return False

        # Guard clause: index out of range
        if criterion_index >= len(card['acceptance_criteria']):
            return False

        card['acceptance_criteria'][criterion_index]['status'] = 'verified'
        card['acceptance_criteria'][criterion_index]['verified_by'] = verified_by

        return True
