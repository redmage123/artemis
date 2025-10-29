from artemis_logger import get_logger
logger = get_logger('status_handler')
'\nWHY: Handle status check requests for tasks\nRESPONSIBILITY: Query checkpoints and format progress naturally\nPATTERNS: Repository (checkpoint access), Guard Clauses\n\nStatus handler retrieves task progress and explains it conversationally.\n'
from typing import Dict, Any
from chat.models import ChatContext
from kanban_manager import KanbanBoard
from checkpoint_manager import CheckpointManager

class StatusHandler:
    """
    Handles status check requests.

    WHY: Users want progress updates in natural language, not raw data.
    PATTERNS: Repository (checkpoint/Kanban access), Guard clauses.
    """

    def __init__(self, kanban: KanbanBoard, verbose: bool=False):
        """
        Initialize status handler.

        Args:
            kanban: Kanban board for card lookup
            verbose: Enable verbose logging
        """
        self.kanban = kanban
        self.verbose = verbose

    def handle(self, intent: Dict[str, Any], context: ChatContext) -> str:
        """
        Handle status check requests.

        WHY: Converts checkpoint data into readable progress explanation.

        Args:
            intent: Intent classification with optional card_id
            context: Conversation context

        Returns:
            Natural language status update

        Example:
            >>> handler = StatusHandler(kanban)
            >>> response = handler.handle(
            ...     {"parameters": {"card_id": "card-123"}},
            ...     context
            ... )
        """
        params = intent.get('parameters', {})
        card_id = params.get('card_id') or context.active_card_id
        if not card_id:
            return 'Which task? Give me a card ID, or I can check your most recent one if you just created something.'
        return self._get_status(card_id)

    def _get_status(self, card_id: str) -> str:
        """
        Get status for card.

        WHY: Separation allows guard clause in caller.

        Args:
            card_id: Card ID to check

        Returns:
            Status explanation
        """
        try:
            checkpoint_mgr = CheckpointManager(card_id, verbose=False)
            if not checkpoint_mgr.can_resume():
                return self._check_kanban_status(card_id)
            checkpoint = checkpoint_mgr.resume()
            progress = checkpoint_mgr.get_progress()
            return self._format_progress(progress)
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[StatusHandler] Status check failed: {e}', 'INFO')
            return 'Having trouble checking that one. The task might not exist yet, or there could be a system issue.'

    def _check_kanban_status(self, card_id: str) -> str:
        """
        Check Kanban board if no checkpoint exists.

        WHY: Provides status even before pipeline starts.

        Args:
            card_id: Card ID

        Returns:
            Status message
        """
        card = self.kanban.get_card(card_id)
        if not card:
            return f"Can't find {card_id}. Double-check the ID?"
        status = card.get('status', 'Unknown')
        return f"That task is {status.lower()}. Haven't started the pipeline yet - want me to kick it off?"

    def _format_progress(self, progress: Dict[str, Any]) -> str:
        """
        Format progress data naturally.

        WHY: Raw percentages are less informative than contextual explanations.

        Args:
            progress: Progress dict from checkpoint

        Returns:
            Natural language explanation

        Example:
            >>> handler._format_progress({
            ...     "stages_completed": 5,
            ...     "total_stages": 10,
            ...     "progress_percent": 50,
            ...     "current_stage": "testing"
            ... })
            'Making good progress. 5/10 stages complete, currently handling testing.'
        """
        completed = progress['stages_completed']
        total = progress['total_stages']
        percent = progress['progress_percent']
        current = progress.get('current_stage', 'finishing up')
        progress_messages = [(100, lambda: f"That one's done! Finished all {total} stages."), (75, lambda: f'Almost there - {completed}/{total} stages done. Working on {current} now.'), (50, lambda: f'Making good progress. {completed}/{total} stages complete, currently handling {current}.'), (25, lambda: f'Getting started. Finished {completed}/{total} stages, now on {current}.'), (0, lambda: f'Just started - {completed}/{total} stages done. Currently working through {current}.')]
        for threshold, message_func in progress_messages:
            if percent >= threshold:
                return message_func()
        return f'{completed}/{total} stages complete'