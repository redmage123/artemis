#!/usr/bin/env python3
"""
Module: kanban/board.py

WHY: Provides centralized board state management, enforces Agile best practices
     (WIP limits, DoD tracking), and enables metrics collection for sprint planning
     and retrospectives.

RESPONSIBILITY:
- Load and persist board state to JSON file
- Card CRUD operations (create, read, update, delete, move)
- Sprint management (create, start, complete sprints)
- WIP limit enforcement with violations tracking
- Metrics calculation (cycle time, velocity, throughput)
- Card blocking/unblocking workflow
- Definition of Done (DoD) validation
- Test status tracking per card
- Board visualization and reporting

PATTERNS:
- Repository Pattern: Combines data access (load/save JSON) with business logic
- Active Record: Board object manages its own persistence
- Guard Clauses: Early returns prevent nested conditionals

INTEGRATION:
- Used by ArtemisOrchestrator for card lifecycle management
- Used by sprint planning stages to assign work
- Used by developer agents to update progress
- Provides data for retrospectives and planning poker
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from artemis_exceptions import (
    KanbanBoardError,
    KanbanCardNotFoundError,
    FileReadError,
    FileWriteError,
    wrap_exception
)
from artemis_constants import KANBAN_BOARD_PATH
from debug_mixin import DebugMixin
from kanban.card_builder import CardBuilder

# Board file path (now using constant from artemis_constants)
BOARD_PATH = str(KANBAN_BOARD_PATH)


class KanbanBoard(DebugMixin):
    """
    Manages all Kanban board operations for Artemis Agile workflow

    Why it exists: Provides centralized board state management, enforces Agile best
                   practices (WIP limits, DoD tracking), and enables metrics collection
                   for sprint planning and retrospectives.

    Design pattern: Repository Pattern + Active Record
    Why this design: Combines data access (load/save JSON) with business logic
                     (WIP validation, metrics calculation) for simplicity.

    Responsibilities:
    - Load and persist board state to JSON file
    - Card CRUD operations (create, read, update, delete, move)
    - Sprint management (create, start, complete sprints)
    - WIP limit enforcement with violations tracking
    - Metrics calculation (cycle time, velocity, throughput)
    - Card blocking/unblocking workflow
    - Definition of Done (DoD) validation
    - Test status tracking per card
    - Board visualization and reporting

    Key Features:
    - Supports both dict and list column formats (backward compatibility)
    - Automatic timestamp tracking for cycle time calculation
    - History tracking for every card state change
    - Metrics auto-update on card completion
    - Generator expressions for performance (early termination on searches)

    Integration points:
    - Used by ArtemisOrchestrator for card lifecycle management
    - Used by sprint planning stages to assign work
    - Used by developer agents to update progress
    - Provides data for retrospectives and planning poker
    """

    def __init__(self, board_path: str = BOARD_PATH):
        """
        Initialize KanbanBoard with JSON file backend

        Why separate board_path param: Allows testing with different board files
                                       without modifying constants.

        Args:
            board_path: Path to kanban_board.json file (defaults to constant)
        """
        DebugMixin.__init__(self, component_name="kanban")
        self.board_path = board_path
        self.board = self._load_board()

    def _load_board(self) -> Dict:
        """
        Load board state from JSON file with backward compatibility

        Why needed: Reads persisted board state, ensuring metrics field exists
                    for older board versions that might not have it.

        What it does:
        - Validates board file exists
        - Loads JSON into memory
        - Adds metrics field if missing (backward compatibility)
        - Wraps I/O errors in custom exceptions with context

        Returns:
            Board dictionary with columns, metrics, sprints, etc.

        Raises:
            KanbanBoardError: If file not found
            FileReadError: If JSON parsing fails

        Design note: Uses wrap_exception to preserve original error while adding
                     Artemis-specific context for better debugging.
        """
        if not os.path.exists(self.board_path):
            raise KanbanBoardError(
                f"Kanban board not found at {self.board_path}",
                context={"board_path": self.board_path}
            )

        try:
            with open(self.board_path, 'r') as f:
                board = json.load(f)

                # Ensure metrics field exists (for backward compatibility)
                if 'metrics' not in board:
                    board['metrics'] = {
                        'cycle_time_avg_hours': 0,
                        'cycle_time_min_hours': 0,
                        'cycle_time_max_hours': 0,
                        'cards_completed': 0,
                        'throughput_current_sprint': 0,
                        'velocity_current_sprint': 0,
                        'wip_violations_count': 0,
                        'blocked_items_count': 0
                    }

                return board
        except Exception as e:
            raise wrap_exception(
                e,
                FileReadError,
                f"Failed to read Kanban board",
                context={"board_path": self.board_path}
            )

    def _save_board(self) -> None:
        """Save board to JSON file"""
        self.board['last_updated'] = datetime.utcnow().isoformat() + 'Z'

        with open(self.board_path, 'w') as f:
            json.dump(self.board, f, indent=2)

    def _find_card(self, card_id: str) -> tuple[Optional[Dict], Optional[str]]:
        """Find a card by ID, return (card, column_id)"""
        columns = self.board.get('columns', {})

        # Handle dict format
        if isinstance(columns, dict):
            # Use generator expression for early termination on first match
            # Note: CardBuilder creates cards with 'task_id', not 'card_id'
            result = next(
                ((card, column_id)
                 for column_id, column_data in columns.items()
                 for card in column_data.get('cards', [])
                 if card.get('task_id') == card_id or card.get('card_id') == card_id),
                (None, None)
            )
            return result

        # Handle list format
        result = next(
            ((card, column.get('column_id'))
             for column in columns
             for card in column.get('cards', [])
             if card.get('task_id') == card_id or card.get('card_id') == card_id),
            (None, None)
        )
        return result

    def _get_column(self, column_id: str) -> Optional[Dict]:
        """Get column by ID"""
        # Handle both dict and list formats
        columns = self.board.get('columns', {})
        if isinstance(columns, dict):
            # Dict format: {column_id: {name, wip_limit, cards}}
            return columns.get(column_id)

        # List format: [{column_id, name, wip_limit, cards}]
        return next((column for column in columns if column.get('column_id') == column_id), None)

    def new_card(self, task_id: str, title: str) -> CardBuilder:
        """
        Create a new card using Builder pattern (RECOMMENDED)

        Usage:
            card_dict = (board.new_card("TASK-001", "Add feature")
                .with_description("Implement API")
                .with_priority("high")
                .with_story_points(8)
                .build())

            board.add_card(card_dict)

        Args:
            task_id: Unique task identifier
            title: Card title

        Returns:
            CardBuilder instance for fluent API
        """
        return CardBuilder(task_id, title)

    def add_card(self, card: Dict) -> Dict:
        """
        Add a pre-built card to the backlog

        Args:
            card: Card dictionary (from CardBuilder.build())

        Returns:
            Added card dictionary

        Raises:
            KanbanBoardError: If backlog column not found
        """
        self.debug_log("Adding card to backlog", card_id=card.get('card_id', 'unknown'), task_id=card.get('task_id', 'unknown'))

        backlog = self._get_column("backlog")
        if not backlog:
            raise KanbanBoardError(
                "Backlog column not found",
                context={"board_path": self.board_path}
            )

        backlog['cards'].append(card)
        self._save_board()

        self.debug_log("Card added successfully", card_id=card.get('card_id', 'unknown'))
        return card

    def move_card(
        self,
        card_id: str,
        to_column: str,
        agent: str = "system",
        comment: str = ""
    ) -> bool:
        """
        Move a card between columns with WIP enforcement and metrics tracking

        Why needed: Core workflow operation that transitions cards through pipeline stages
                    while enforcing Agile practices (WIP limits) and collecting metrics.

        What it does:
        - Finds card in current column
        - Validates destination column exists
        - Checks WIP limit (warns but allows, tracks violations)
        - Removes card from source column
        - Updates card timestamps and column tracking
        - Adds history entry for audit trail
        - Adds card to destination column
        - Calculates cycle time if moving to 'done'
        - Updates board-level metrics
        - Persists changes to JSON file

        Args:
            card_id: Card identifier to move (task_id or card_id)
            to_column: Destination column ID (e.g., 'development', 'review', 'done')
            agent: Name of agent/user performing move (for history tracking)
            comment: Optional comment explaining the move

        Returns:
            True if move succeeded, False if card or column not found

        Side effects:
            - Updates board JSON file
            - Increments WIP violation counter if limit exceeded
            - Updates completion metrics if moved to 'done'
            - Prints status messages to console

        Design decisions:
            - WIP limit is a warning, not a hard block (allows flexibility)
            - Cycle time auto-calculated on completion (no manual tracking needed)
            - History tracking for every move enables detailed retrospectives
            - Dual card_id lookup (task_id or card_id) for backward compatibility
        """
        self.debug_log("Moving card", card_id=card_id, from_column="searching", to_column=to_column, agent=agent)

        card, from_column = self._find_card(card_id)
        if not card:
            print(f"❌ Card {card_id} not found")
            self.debug_log("Card not found", card_id=card_id)
            return False

        to_col = self._get_column(to_column)
        if not to_col:
            print(f"❌ Column {to_column} not found")
            return False

        # Check WIP limit
        if to_col['wip_limit'] is not None:
            if len(to_col['cards']) >= to_col['wip_limit']:
                print(f"⚠️  WIP limit exceeded for {to_column} ({len(to_col['cards'])}/{to_col['wip_limit']})")
                self.board['metrics']['wip_violations_count'] += 1

        # Remove from current column
        from_col = self._get_column(from_column)
        if from_col:
            from_col['cards'] = [c for c in from_col['cards'] if c['card_id'] != card_id]

        # Add to new column
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

        to_col['cards'].append(card)

        # Update metrics if moved to done
        if to_column == "done":
            card['completed_at'] = datetime.utcnow().isoformat() + 'Z'

            # Calculate cycle time
            created = datetime.fromisoformat(card['created_at'].replace('Z', '+00:00'))
            completed = datetime.now(timezone.utc)
            cycle_time_hours = (completed - created).total_seconds() / 3600
            card['cycle_time_hours'] = round(cycle_time_hours, 2)

            # Update board metrics
            self._update_metrics()

        self._save_board()
        print(f"✅ Moved card {card_id} from {from_column} to {to_column}")
        return True

    def update_card(
        self,
        card_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update card fields

        Args:
            card_id: Card to update
            updates: Dictionary of field updates

        Returns:
            True if successful
        """
        card, column = self._find_card(card_id)
        if not card:
            print(f"❌ Card {card_id} not found")
            return False

        # Update fields
        for key, value in updates.items():
            if key in card:
                card[key] = value

        self._save_board()
        print(f"✅ Updated card {card_id}")
        return True

    def block_card(
        self,
        card_id: str,
        reason: str,
        agent: str = "system"
    ) -> bool:
        """
        Mark a card as blocked and move to Blocked column

        Args:
            card_id: Card to block
            reason: Reason for blocking
            agent: Agent reporting the block

        Returns:
            True if successful
        """
        card, from_column = self._find_card(card_id)
        if not card:
            print(f"❌ Card {card_id} not found")
            return False

        card['blocked'] = True
        card['blocked_reason'] = reason

        self.move_card(card_id, "blocked", agent, f"BLOCKED: {reason}")

        # Update metrics
        self.board['metrics']['blocked_items_count'] = len(self._get_column("blocked")['cards'])
        self._save_board()

        print(f"🚫 Blocked card {card_id}: {reason}")
        return True

    def unblock_card(
        self,
        card_id: str,
        move_to_column: str,
        agent: str = "system",
        resolution: str = ""
    ) -> bool:
        """
        Unblock a card and move to specified column

        Args:
            card_id: Card to unblock
            move_to_column: Where to move the card
            agent: Agent unblocking
            resolution: How the block was resolved

        Returns:
            True if successful
        """
        card, column = self._find_card(card_id)
        if not card or column != "blocked":
            print(f"❌ Card {card_id} not in blocked column")
            return False

        card['blocked'] = False
        old_reason = card['blocked_reason']
        card['blocked_reason'] = None

        self.move_card(card_id, move_to_column, agent, f"UNBLOCKED: {resolution}")

        # Update metrics
        self.board['metrics']['blocked_items_count'] = len(self._get_column("blocked")['cards'])
        self._save_board()

        print(f"✅ Unblocked card {card_id} (was: {old_reason})")
        return True

    def update_test_status(
        self,
        card_id: str,
        test_status: Dict[str, Any]
    ) -> bool:
        """
        Update test status for a card

        Args:
            card_id: Card to update
            test_status: Dictionary with test status fields

        Returns:
            True if successful
        """
        card, column = self._find_card(card_id)
        if not card:
            print(f"❌ Card {card_id} not found")
            return False

        card['test_status'].update(test_status)
        self._save_board()

        print(f"✅ Updated test status for card {card_id}")
        return True

    def verify_acceptance_criterion(
        self,
        card_id: str,
        criterion_index: int,
        verified_by: str
    ) -> bool:
        """
        Mark an acceptance criterion as verified

        Args:
            card_id: Card ID
            criterion_index: Index of criterion to verify
            verified_by: Agent verifying

        Returns:
            True if successful
        """
        card, column = self._find_card(card_id)
        if not card:
            print(f"❌ Card {card_id} not found")
            return False

        if criterion_index >= len(card['acceptance_criteria']):
            print(f"❌ Criterion index {criterion_index} out of range")
            return False

        card['acceptance_criteria'][criterion_index]['status'] = 'verified'
        card['acceptance_criteria'][criterion_index]['verified_by'] = verified_by

        self._save_board()
        print(f"✅ Verified acceptance criterion for card {card_id}")
        return True

    def _update_metrics(self) -> None:
        """Recalculate board metrics"""
        done_column = self._get_column("done")
        if not done_column:
            return

        done_cards = done_column['cards']

        if not done_cards:
            return

        cycle_times = [c.get('cycle_time_hours', 0) for c in done_cards if 'cycle_time_hours' in c]
        if cycle_times:
            self.board['metrics']['cycle_time_avg_hours'] = round(sum(cycle_times) / len(cycle_times), 2)
            self.board['metrics']['cycle_time_min_hours'] = round(min(cycle_times), 2)
            self.board['metrics']['cycle_time_max_hours'] = round(max(cycle_times), 2)

        self.board['metrics']['cards_completed'] = len(done_cards)
        self.board['metrics']['throughput_current_sprint'] = len(done_cards)

        # Calculate velocity
        velocity = sum(c.get('story_points', 0) for c in done_cards)
        self.board['metrics']['velocity_current_sprint'] = velocity

        if self.board.get('current_sprint'):
            self.board['current_sprint']['completed_story_points'] = velocity

    def get_board_summary(self) -> Dict:
        """Get summary of board status"""
        summary = {
            "board_id": self.board['board_id'],
            "last_updated": self.board['last_updated'],
            "columns": []
        }

        for column in self.board['columns']:
            summary['columns'].append({
                "name": column['name'],
                "column_id": column['column_id'],
                "card_count": len(column['cards']),
                "wip_limit": column['wip_limit'],
                "cards": [
                    {
                        "card_id": c['card_id'],
                        "title": c['title'],
                        "priority": c['priority'],
                        "blocked": c.get('blocked', False)
                    }
                    for c in column['cards']
                ]
            })

        summary['metrics'] = self.board['metrics']
        summary['current_sprint'] = self.board.get('current_sprint')

        return summary

    def print_board(self) -> None:
        """Print visual representation of board"""
        print("\n" + "="*80)
        print(f"  KANBAN BOARD: {self.board['board_id']}")
        print(f"  Last Updated: {self.board['last_updated']}")
        if self.board.get('current_sprint'):
            sprint = self.board['current_sprint']
            print(f"  Sprint: {sprint['sprint_id']} ({sprint['completed_story_points']}/{sprint['committed_story_points']} points)")
        print("="*80)

        for column in self.board['columns']:
            wip_info = f"(WIP: {len(column['cards'])}/{column['wip_limit']})" if column['wip_limit'] else f"({len(column['cards'])})"
            print(f"\n📋 {column['name']} {wip_info}")
            print("-" * 80)

            if not column['cards']:
                print("  (empty)")
            else:
                for card in column['cards']:
                    blocked_indicator = "🚫 " if card.get('blocked', False) else ""
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(card['priority'], "⚪")
                    print(f"  {blocked_indicator}{priority_emoji} {card['card_id']} - {card['title']}")
                    print(f"     Priority: {card['priority']} | Points: {card.get('story_points', 'N/A')} | Agents: {', '.join(card['assigned_agents'][:2])}")
                    if card.get('test_status'):
                        coverage = card['test_status'].get('test_coverage_percent', 0)
                        print(f"     Tests: {coverage}% coverage")

        print("\n" + "="*80)
        print("METRICS")
        print("="*80)
        metrics = self.board['metrics']
        print(f"  Cycle Time: {metrics.get('cycle_time_avg_hours', 0):.2f}h avg")
        print(f"  Throughput: {metrics.get('throughput_current_sprint', 0)} cards this sprint")
        print(f"  Velocity: {metrics.get('velocity_current_sprint', 0)} story points")
        print(f"  Blocked: {metrics.get('blocked_items_count', 0)} items")
        print(f"  WIP Violations: {metrics.get('wip_violations_count', 0)}")
        print("="*80 + "\n")

    def create_sprint(
        self,
        sprint_number: int,
        start_date: str,
        end_date: str,
        committed_story_points: int,
        features: List[Dict] = None
    ) -> Dict:
        """
        Create a new sprint

        Args:
            sprint_number: Sprint number (e.g., 1, 2, 3)
            start_date: Sprint start date (YYYY-MM-DD)
            end_date: Sprint end date (YYYY-MM-DD)
            committed_story_points: Total story points committed for sprint
            features: List of features/stories in sprint

        Returns:
            Created sprint dict
        """
        self.debug_log("Creating sprint", sprint_number=sprint_number, start_date=start_date, end_date=end_date, points=committed_story_points)

        sprint = {
            'sprint_id': f"sprint-{sprint_number}",
            'sprint_number': sprint_number,
            'start_date': start_date,
            'end_date': end_date,
            'committed_story_points': committed_story_points,
            'completed_story_points': 0,
            'status': 'planned',  # planned, active, completed
            'features': features or [],
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }

        # Initialize sprints list if not exists
        if 'sprints' not in self.board:
            self.board['sprints'] = []

        # Add sprint to board
        self.board['sprints'].append(sprint)
        self._save_board()

        self.debug_log("Sprint created", sprint_id=sprint['sprint_id'])
        return sprint

    def start_sprint(self, sprint_number: int) -> Dict:
        """
        Start a sprint (set as current sprint)

        Args:
            sprint_number: Sprint number to start

        Returns:
            Started sprint dict

        Raises:
            KanbanBoardError: If sprint not found or another sprint is active
        """
        if 'sprints' not in self.board:
            raise KanbanBoardError(
                "No sprints found on board",
                context={"sprint_number": sprint_number}
            )

        # Check if another sprint is active
        current_sprint = self.board.get('current_sprint')
        if current_sprint and current_sprint.get('status') == 'active':
            raise KanbanBoardError(
                f"Sprint {current_sprint.get('sprint_number')} is already active",
                context={"active_sprint": current_sprint.get('sprint_number')}
            )

        # Find sprint using next() for early termination
        sprint = next(
            (s for s in self.board['sprints'] if s.get('sprint_number') == sprint_number),
            None
        )

        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Start sprint
        sprint['status'] = 'active'
        sprint['started_at'] = datetime.utcnow().isoformat() + 'Z'
        self.board['current_sprint'] = sprint

        self._save_board()
        return sprint

    def complete_sprint(
        self,
        sprint_number: int,
        completed_story_points: int,
        retrospective_notes: Optional[str] = None
    ) -> Dict:
        """
        Complete a sprint and run retrospective

        Args:
            sprint_number: Sprint number to complete
            completed_story_points: Actual story points completed
            retrospective_notes: Optional retrospective notes

        Returns:
            Completed sprint dict

        Raises:
            KanbanBoardError: If sprint not found
        """
        if 'sprints' not in self.board:
            raise KanbanBoardError(
                "No sprints found on board",
                context={"sprint_number": sprint_number}
            )

        # Find sprint using next() for early termination
        sprint = next(
            (s for s in self.board['sprints'] if s.get('sprint_number') == sprint_number),
            None
        )

        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Complete sprint
        sprint['status'] = 'completed'
        sprint['completed_at'] = datetime.utcnow().isoformat() + 'Z'
        sprint['completed_story_points'] = completed_story_points
        sprint['velocity'] = (completed_story_points / max(sprint['committed_story_points'], 1)) * 100

        if retrospective_notes:
            sprint['retrospective_notes'] = retrospective_notes

        # Clear current sprint if this was active
        if self.board.get('current_sprint', {}).get('sprint_number') == sprint_number:
            self.board['current_sprint'] = None

        self._save_board()
        return sprint

    def get_sprint(self, sprint_number: int) -> Optional[Dict]:
        """
        Get sprint by number

        Args:
            sprint_number: Sprint number

        Returns:
            Sprint dict or None if not found
        """
        if 'sprints' not in self.board:
            return None

        # Use next() with generator expression for early termination
        return next(
            (sprint for sprint in self.board['sprints'] if sprint.get('sprint_number') == sprint_number),
            None
        )

    def get_current_sprint(self) -> Optional[Dict]:
        """
        Get the current active sprint

        Returns:
            Current sprint dict or None if no active sprint
        """
        return self.board.get('current_sprint')

    def get_all_sprints(self) -> List[Dict]:
        """
        Get all sprints

        Returns:
            List of all sprints
        """
        return self.board.get('sprints', [])

    def update_sprint_metadata(
        self,
        sprint_number: int,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update sprint metadata

        Args:
            sprint_number: Sprint number
            metadata: Metadata to merge into sprint

        Raises:
            KanbanBoardError: If sprint not found
        """
        sprint = self.get_sprint(sprint_number)
        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Merge metadata
        sprint.update(metadata)
        self._save_board()

    def assign_card_to_sprint(
        self,
        card_id: str,
        sprint_number: int
    ) -> None:
        """
        Assign a card to a sprint

        Args:
            card_id: Card ID to assign
            sprint_number: Sprint number to assign to

        Raises:
            KanbanCardNotFoundError: If card not found
            KanbanBoardError: If sprint not found
        """
        card, _ = self._find_card(card_id)
        if not card:
            raise KanbanCardNotFoundError(
                card_id,
                context={"card_id": card_id}
            )

        sprint = self.get_sprint(sprint_number)
        if not sprint:
            raise KanbanBoardError(
                f"Sprint {sprint_number} not found",
                context={"sprint_number": sprint_number}
            )

        # Update card with sprint assignment
        card['sprint_number'] = sprint_number
        card['assigned_to_sprint'] = sprint['sprint_id']

        self._save_board()

    def get_sprint_backlog(self, sprint_number: int) -> List[Dict]:
        """
        Get all cards assigned to a sprint

        Args:
            sprint_number: Sprint number

        Returns:
            List of cards in sprint backlog
        """
        columns = self.board.get('columns', {})

        # Handle both dict and list formats using list comprehension
        if isinstance(columns, dict):
            cards = [
                card
                for column_data in columns.values()
                for card in column_data.get('cards', [])
                if card.get('sprint_number') == sprint_number
            ]
        else:
            cards = [
                card
                for column in columns
                for card in column.get('cards', [])
                if card.get('sprint_number') == sprint_number
            ]

        return cards

    def get_sprint_velocity(self, sprint_number: int) -> float:
        """
        Calculate sprint velocity (completed story points / committed story points)

        Args:
            sprint_number: Sprint number

        Returns:
            Velocity as percentage (0-100)
        """
        sprint = self.get_sprint(sprint_number)
        if not sprint:
            return 0.0

        committed = sprint.get('committed_story_points', 0)
        completed = sprint.get('completed_story_points', 0)

        if committed == 0:
            return 0.0

        return (completed / committed) * 100

    def get_cards_in_column(self, column_id: str) -> List[Dict]:
        """
        Get all cards in a specific column

        Args:
            column_id: Column to get cards from

        Returns:
            List of card dictionaries
        """
        column = self._get_column(column_id)
        if not column:
            return []

        return column.get('cards', [])

    def get_pending_cards(self) -> List[Dict]:
        """
        Get all pending cards (from backlog and development columns)

        Returns:
            List of card dictionaries that need processing
        """
        pending_cards = []

        # Get cards from backlog
        backlog_cards = self.get_cards_in_column('backlog')
        pending_cards.extend(backlog_cards)

        # Get cards from development (in progress but may need routing)
        # Note: We only include cards that are not blocked
        dev_cards = self.get_cards_in_column('development')
        for card in dev_cards:
            if not card.get('blocked', False):
                pending_cards.append(card)

        return pending_cards

    def get_all_incomplete_cards(self) -> List[Dict]:
        """
        Get all cards that are not in 'done' column

        Returns:
            List of card dictionaries that are incomplete
        """
        incomplete_cards = []
        columns = self.board.get('columns', {})

        if isinstance(columns, dict):
            for column_id, column_data in columns.items():
                if column_id != 'done':  # Skip done column
                    cards = column_data.get('cards', [])
                    incomplete_cards.extend(cards)
        else:
            # List format
            for column in columns:
                if column.get('column_id') != 'done':
                    cards = column.get('cards', [])
                    incomplete_cards.extend(cards)

        return incomplete_cards

    def has_incomplete_cards(self) -> bool:
        """
        Check if there are any incomplete cards on the board

        Returns:
            True if there are cards not in 'done' column
        """
        return len(self.get_all_incomplete_cards()) > 0
