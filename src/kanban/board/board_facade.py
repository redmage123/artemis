from artemis_logger import get_logger
logger = get_logger('board_facade')
'\nModule: kanban/board/board_facade.py\n\nWHY: Main orchestrator providing unified API for all board operations\n     Coordinates between specialized modules\n\nRESPONSIBILITY:\n- Unified API for all board operations\n- Coordinate between persistence, operations, and metrics\n- Maintain board state in memory\n- Delegate to specialized modules\n\nPATTERNS:\n- Facade Pattern: Simplifies complex subsystem interactions\n- Delegation: Forwards operations to specialized modules\n'
from typing import Dict, List, Optional, Any
from artemis_constants import KANBAN_BOARD_PATH
from debug_mixin import DebugMixin
from kanban.card_builder import CardBuilder
from kanban.board.persistence import BoardPersistence
from kanban.board.models import BoardModels
from kanban.board.card_operations import CardOperations
from kanban.board.sprint_manager import SprintManager
from kanban.board.metrics_calculator import MetricsCalculator
from kanban.board.board_visualizer import BoardVisualizer
BOARD_PATH = str(KANBAN_BOARD_PATH)

class KanbanBoard(DebugMixin):
    """
    Facade for all Kanban board operations.

    WHY: Provides centralized board state management, enforces Agile best
         practices (WIP limits, DoD tracking), and enables metrics collection
         for sprint planning and retrospectives.

    RESPONSIBILITY:
    - Coordinate all board operations
    - Maintain board state
    - Delegate to specialized modules
    - Provide backward-compatible API

    PATTERNS:
    - Facade Pattern: Unified interface to subsystems
    - Repository Pattern: Data persistence abstraction
    - Delegation: Forward operations to specialists

    Integration points:
    - Used by ArtemisOrchestrator for card lifecycle management
    - Used by sprint planning stages to assign work
    - Used by developer agents to update progress
    - Provides data for retrospectives and planning poker
    """

    def __init__(self, board_path: str=BOARD_PATH):
        """
        Initialize KanbanBoard with JSON file backend.

        WHY: Loads board state and initializes debug logging

        Args:
            board_path: Path to kanban_board.json file (defaults to constant)
        """
        DebugMixin.__init__(self, component_name='kanban')
        self.board_path = board_path
        self.board = BoardPersistence.load_board(board_path)

    def _save_board(self) -> None:
        """
        Save board to JSON file.

        WHY: Persists board state after operations
        """
        BoardPersistence.save_board(self.board, self.board_path)

    def new_card(self, task_id: str, title: str) -> CardBuilder:
        """
        Create a new card using Builder pattern (RECOMMENDED).

        WHY: Provides fluent API for card creation

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
        Add a pre-built card to the backlog.

        WHY: Creates new cards in the system

        Args:
            card: Card dictionary (from CardBuilder.build())

        Returns:
            Added card dictionary
        """
        self.debug_log('Adding card to backlog', card_id=card.get('card_id', 'unknown'), task_id=card.get('task_id', 'unknown'))
        result = CardOperations.add_card(self.board, card)
        self._save_board()
        self.debug_log('Card added successfully', card_id=card.get('card_id', 'unknown'))
        return result

    def move_card(self, card_id: str, to_column: str, agent: str='system', comment: str='') -> bool:
        """
        Move a card between columns with WIP enforcement.

        WHY: Core workflow operation for card transitions
        PERFORMANCE: O(n) for card search, O(1) for move

        Args:
            card_id: Card identifier to move (task_id or card_id)
            to_column: Destination column ID
            agent: Name of agent/user performing move
            comment: Optional comment explaining the move

        Returns:
            True if move succeeded, False if card or column not found
        """
        self.debug_log('Moving card', card_id=card_id, from_column='searching', to_column=to_column, agent=agent)
        success = CardOperations.move_card(self.board, card_id, to_column, agent, comment)
        if not success:
            
            logger.log(f'❌ Card {card_id} move failed', 'INFO')
            self.debug_log('Card move failed', card_id=card_id)
            return False
        if to_column == 'done':
            MetricsCalculator.update_metrics(self.board)
        self._save_board()
        
        logger.log(f'✅ Moved card {card_id} to {to_column}', 'INFO')
        return True

    def update_card(self, card_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update card fields.

        WHY: Allows partial card updates

        Args:
            card_id: Card to update
            updates: Dictionary of field updates

        Returns:
            True if successful
        """
        success = CardOperations.update_card(self.board, card_id, updates)
        if not success:
            
            logger.log(f'❌ Card {card_id} not found', 'INFO')
            return False
        self._save_board()
        
        logger.log(f'✅ Updated card {card_id}', 'INFO')
        return True

    def block_card(self, card_id: str, reason: str, agent: str='system') -> bool:
        """
        Mark a card as blocked and move to Blocked column.

        WHY: Tracks blockers in workflow

        Args:
            card_id: Card to block
            reason: Reason for blocking
            agent: Agent reporting the block

        Returns:
            True if successful
        """
        success = CardOperations.block_card(self.board, card_id, reason, agent)
        if not success:
            
            logger.log(f'❌ Card {card_id} not found', 'INFO')
            return False
        self._save_board()
        
        logger.log(f'🚫 Blocked card {card_id}: {reason}', 'INFO')
        return True

    def unblock_card(self, card_id: str, move_to_column: str, agent: str='system', resolution: str='') -> bool:
        """
        Unblock a card and move to specified column.

        WHY: Resolves blockers and resumes workflow

        Args:
            card_id: Card to unblock
            move_to_column: Where to move the card
            agent: Agent unblocking
            resolution: How the block was resolved

        Returns:
            True if successful
        """
        success = CardOperations.unblock_card(self.board, card_id, move_to_column, agent, resolution)
        if not success:
            
            logger.log(f'❌ Card {card_id} not in blocked column', 'INFO')
            return False
        self._save_board()
        
        logger.log(f'✅ Unblocked card {card_id}', 'INFO')
        return True

    def update_test_status(self, card_id: str, test_status: Dict[str, Any]) -> bool:
        """
        Update test status for a card.

        WHY: Tracks testing progress

        Args:
            card_id: Card to update
            test_status: Dictionary with test status fields

        Returns:
            True if successful
        """
        success = CardOperations.update_test_status(self.board, card_id, test_status)
        if not success:
            
            logger.log(f'❌ Card {card_id} not found', 'INFO')
            return False
        self._save_board()
        
        logger.log(f'✅ Updated test status for card {card_id}', 'INFO')
        return True

    def verify_acceptance_criterion(self, card_id: str, criterion_index: int, verified_by: str) -> bool:
        """
        Mark an acceptance criterion as verified.

        WHY: Tracks acceptance criteria completion

        Args:
            card_id: Card ID
            criterion_index: Index of criterion to verify
            verified_by: Agent verifying

        Returns:
            True if successful
        """
        success = CardOperations.verify_acceptance_criterion(self.board, card_id, criterion_index, verified_by)
        if not success:
            
            logger.log(f'❌ Verification failed for card {card_id}', 'INFO')
            return False
        self._save_board()
        
        logger.log(f'✅ Verified acceptance criterion for card {card_id}', 'INFO')
        return True

    def create_sprint(self, sprint_number: int, start_date: str, end_date: str, committed_story_points: int, features: Optional[List[Dict]]=None) -> Dict:
        """
        Create a new sprint.

        WHY: Initializes sprint structure

        Args:
            sprint_number: Sprint number (e.g., 1, 2, 3)
            start_date: Sprint start date (YYYY-MM-DD)
            end_date: Sprint end date (YYYY-MM-DD)
            committed_story_points: Total story points committed for sprint
            features: List of features/stories in sprint

        Returns:
            Created sprint dict
        """
        self.debug_log('Creating sprint', sprint_number=sprint_number, start_date=start_date, end_date=end_date, points=committed_story_points)
        sprint = SprintManager.create_sprint(self.board, sprint_number, start_date, end_date, committed_story_points, features)
        self._save_board()
        self.debug_log('Sprint created', sprint_id=sprint['sprint_id'])
        return sprint

    def start_sprint(self, sprint_number: int) -> Dict:
        """
        Start a sprint (set as current sprint).

        WHY: Activates sprint for tracking

        Args:
            sprint_number: Sprint number to start

        Returns:
            Started sprint dict
        """
        sprint = SprintManager.start_sprint(self.board, sprint_number)
        self._save_board()
        return sprint

    def complete_sprint(self, sprint_number: int, completed_story_points: int, retrospective_notes: Optional[str]=None) -> Dict:
        """
        Complete a sprint and run retrospective.

        WHY: Finalizes sprint with metrics

        Args:
            sprint_number: Sprint number to complete
            completed_story_points: Actual story points completed
            retrospective_notes: Optional retrospective notes

        Returns:
            Completed sprint dict
        """
        sprint = SprintManager.complete_sprint(self.board, sprint_number, completed_story_points, retrospective_notes)
        self._save_board()
        return sprint

    def get_sprint(self, sprint_number: int) -> Optional[Dict]:
        """Get sprint by number."""
        return SprintManager.get_sprint(self.board, sprint_number)

    def get_current_sprint(self) -> Optional[Dict]:
        """Get the current active sprint."""
        return SprintManager.get_current_sprint(self.board)

    def get_all_sprints(self) -> List[Dict]:
        """Get all sprints."""
        return SprintManager.get_all_sprints(self.board)

    def update_sprint_metadata(self, sprint_number: int, metadata: Dict[str, Any]) -> None:
        """Update sprint metadata."""
        SprintManager.update_sprint_metadata(self.board, sprint_number, metadata)
        self._save_board()

    def assign_card_to_sprint(self, card_id: str, sprint_number: int) -> None:
        """Assign a card to a sprint."""
        SprintManager.assign_card_to_sprint(self.board, card_id, sprint_number)
        self._save_board()

    def get_sprint_backlog(self, sprint_number: int) -> List[Dict]:
        """Get all cards assigned to a sprint."""
        return BoardModels.get_sprint_backlog_cards(self.board, sprint_number)

    def get_sprint_velocity(self, sprint_number: int) -> float:
        """Calculate sprint velocity."""
        return SprintManager.get_sprint_velocity(self.board, sprint_number)

    def get_cards_in_column(self, column_id: str) -> List[Dict]:
        """Get all cards in a specific column."""
        return BoardModels.get_cards_in_column(self.board, column_id)

    def get_pending_cards(self) -> List[Dict]:
        """Get all pending cards (backlog + non-blocked development)."""
        return BoardModels.get_pending_cards(self.board)

    def get_all_incomplete_cards(self) -> List[Dict]:
        """Get all cards that are not in 'done' column."""
        return BoardModels.get_all_incomplete_cards(self.board)

    def has_incomplete_cards(self) -> bool:
        """Check if there are any incomplete cards on the board."""
        return len(self.get_all_incomplete_cards()) > 0

    def get_board_summary(self) -> Dict:
        """Get summary of board status."""
        return MetricsCalculator.get_board_summary(self.board)

    def print_board(self) -> None:
        """Print visual representation of board."""
        BoardVisualizer.print_board(self.board)

    def _find_card(self, card_id: str) -> tuple:
        """Find a card by ID (backward compatibility)."""
        return BoardModels.find_card(self.board, card_id)

    def _get_column(self, column_id: str) -> Optional[Dict]:
        """Get column by ID (backward compatibility)."""
        return BoardModels.get_column(self.board, column_id)

    def _update_metrics(self) -> None:
        """Recalculate board metrics (backward compatibility)."""
        MetricsCalculator.update_metrics(self.board)