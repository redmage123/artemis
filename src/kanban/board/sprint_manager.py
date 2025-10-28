#!/usr/bin/env python3
"""
Module: kanban/board/sprint_manager.py

WHY: Manages sprint lifecycle (create, start, complete)
     Tracks sprint metadata and velocity calculations

RESPONSIBILITY:
- Sprint creation and lifecycle management
- Sprint backlog assignment
- Velocity calculations
- Sprint metadata updates

PATTERNS:
- Facade Pattern: Simplifies sprint operations
- Guard Clauses: Early validation returns
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from artemis_exceptions import KanbanBoardError, KanbanCardNotFoundError
from kanban.board.models import BoardModels


class SprintManager:
    """
    Sprint lifecycle and metadata management.

    WHY: Centralizes sprint-related operations
    RESPONSIBILITY: Sprint CRUD and metrics
    PATTERNS: Facade pattern
    """

    @staticmethod
    def create_sprint(
        board: Dict,
        sprint_number: int,
        start_date: str,
        end_date: str,
        committed_story_points: int,
        features: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Create a new sprint.

        WHY: Initializes sprint structure
        PERFORMANCE: O(1) append operation

        Args:
            board: Board dictionary
            sprint_number: Sprint number (e.g., 1, 2, 3)
            start_date: Sprint start date (YYYY-MM-DD)
            end_date: Sprint end date (YYYY-MM-DD)
            committed_story_points: Total story points committed
            features: List of features/stories in sprint

        Returns:
            Created sprint dictionary
        """
        sprint = {
            'sprint_id': f"sprint-{sprint_number}",
            'sprint_number': sprint_number,
            'start_date': start_date,
            'end_date': end_date,
            'committed_story_points': committed_story_points,
            'completed_story_points': 0,
            'status': 'planned',
            'features': features or [],
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }

        # Initialize sprints list if not exists
        if 'sprints' not in board:
            board['sprints'] = []

        board['sprints'].append(sprint)
        return sprint

    @staticmethod
    def start_sprint(board: Dict, sprint_number: int) -> Dict:
        """
        Start a sprint (set as current sprint).

        WHY: Activates sprint for tracking
        PERFORMANCE: O(n) for sprint search

        Args:
            board: Board dictionary
            sprint_number: Sprint number to start

        Returns:
            Started sprint dictionary

        Raises:
            KanbanBoardError: If sprint not found or another sprint is active
        """
        # Guard clause: no sprints
        if 'sprints' not in board:
            raise KanbanBoardError(
                "No sprints found on board",
                context={"sprint_number": sprint_number}
            )

        # Guard clause: another sprint active
        current_sprint = board.get('current_sprint')
        if current_sprint and current_sprint.get('status') == 'active':
            raise KanbanBoardError(
                f"Sprint {current_sprint.get('sprint_number')} is already active",
                context={"active_sprint": current_sprint.get('sprint_number')}
            )

        # Find sprint using generator
        sprint = next(
            (s for s in board['sprints'] if s.get('sprint_number') == sprint_number),
            None
        )

        # Guard clause: sprint not found
        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Start sprint
        sprint['status'] = 'active'
        sprint['started_at'] = datetime.utcnow().isoformat() + 'Z'
        board['current_sprint'] = sprint

        return sprint

    @staticmethod
    def complete_sprint(
        board: Dict,
        sprint_number: int,
        completed_story_points: int,
        retrospective_notes: Optional[str] = None
    ) -> Dict:
        """
        Complete a sprint and run retrospective.

        WHY: Finalizes sprint with metrics
        PERFORMANCE: O(n) for sprint search

        Args:
            board: Board dictionary
            sprint_number: Sprint number to complete
            completed_story_points: Actual story points completed
            retrospective_notes: Optional retrospective notes

        Returns:
            Completed sprint dictionary

        Raises:
            KanbanBoardError: If sprint not found
        """
        # Guard clause: no sprints
        if 'sprints' not in board:
            raise KanbanBoardError(
                "No sprints found on board",
                context={"sprint_number": sprint_number}
            )

        # Find sprint using generator
        sprint = next(
            (s for s in board['sprints'] if s.get('sprint_number') == sprint_number),
            None
        )

        # Guard clause: sprint not found
        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Complete sprint
        sprint['status'] = 'completed'
        sprint['completed_at'] = datetime.utcnow().isoformat() + 'Z'
        sprint['completed_story_points'] = completed_story_points
        sprint['velocity'] = (
            completed_story_points / max(sprint['committed_story_points'], 1)
        ) * 100

        if retrospective_notes:
            sprint['retrospective_notes'] = retrospective_notes

        # Clear current sprint if this was active
        if board.get('current_sprint', {}).get('sprint_number') == sprint_number:
            board['current_sprint'] = None

        return sprint

    @staticmethod
    def get_sprint(board: Dict, sprint_number: int) -> Optional[Dict]:
        """
        Get sprint by number.

        WHY: Sprint lookup operation
        PERFORMANCE: O(n) with early termination

        Args:
            board: Board dictionary
            sprint_number: Sprint number

        Returns:
            Sprint dictionary or None
        """
        # Guard clause: no sprints
        if 'sprints' not in board:
            return None

        return next(
            (sprint for sprint in board['sprints'] if sprint.get('sprint_number') == sprint_number),
            None
        )

    @staticmethod
    def get_current_sprint(board: Dict) -> Optional[Dict]:
        """
        Get the current active sprint.

        WHY: Access to active sprint
        PERFORMANCE: O(1) dictionary lookup

        Returns:
            Current sprint dictionary or None
        """
        return board.get('current_sprint')

    @staticmethod
    def get_all_sprints(board: Dict) -> List[Dict]:
        """
        Get all sprints.

        WHY: Sprint history access
        PERFORMANCE: O(1) list access

        Returns:
            List of all sprints
        """
        return board.get('sprints', [])

    @staticmethod
    def update_sprint_metadata(
        board: Dict,
        sprint_number: int,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update sprint metadata.

        WHY: Allows sprint metadata modifications
        PERFORMANCE: O(n) for sprint search

        Args:
            board: Board dictionary
            sprint_number: Sprint number
            metadata: Metadata to merge into sprint

        Raises:
            KanbanBoardError: If sprint not found
        """
        sprint = SprintManager.get_sprint(board, sprint_number)

        # Guard clause: sprint not found
        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        sprint.update(metadata)

    @staticmethod
    def assign_card_to_sprint(
        board: Dict,
        card_id: str,
        sprint_number: int
    ) -> None:
        """
        Assign a card to a sprint.

        WHY: Sprint backlog management
        PERFORMANCE: O(n) for card and sprint search

        Args:
            board: Board dictionary
            card_id: Card ID to assign
            sprint_number: Sprint number to assign to

        Raises:
            KanbanCardNotFoundError: If card not found
            KanbanBoardError: If sprint not found
        """
        card, _ = BoardModels.find_card(board, card_id)

        # Guard clause: card not found
        if not card:
            raise KanbanCardNotFoundError(
                card_id,
                context={"card_id": card_id}
            )

        sprint = SprintManager.get_sprint(board, sprint_number)

        # Guard clause: sprint not found
        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Update card with sprint assignment
        card['sprint_number'] = sprint_number
        card['assigned_to_sprint'] = sprint['sprint_id']

    @staticmethod
    def get_sprint_velocity(board: Dict, sprint_number: int) -> float:
        """
        Calculate sprint velocity (completed / committed * 100).

        WHY: Sprint performance metric
        PERFORMANCE: O(n) for sprint search

        Args:
            board: Board dictionary
            sprint_number: Sprint number

        Returns:
            Velocity as percentage (0-100)
        """
        sprint = SprintManager.get_sprint(board, sprint_number)

        # Guard clause: sprint not found
        if not sprint:
            return 0.0

        committed = sprint.get('committed_story_points', 0)
        completed = sprint.get('completed_story_points', 0)

        # Guard clause: no commitment
        if committed == 0:
            return 0.0

        return (completed / committed) * 100
