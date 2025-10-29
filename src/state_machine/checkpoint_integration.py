from artemis_logger import get_logger
logger = get_logger('checkpoint_integration')
'\nWHY: Integrate checkpoint/resume functionality for pipeline persistence\nRESPONSIBILITY: Delegate checkpoint operations to CheckpointManager\nPATTERNS: Facade pattern for checkpoint operations, delegation pattern\n'
from datetime import datetime
from typing import Dict, Any, Optional

class CheckpointIntegration:
    """
    Integrates checkpoint/resume functionality with state machine

    Features:
    - Checkpoint creation and restoration
    - Stage checkpoint tracking
    - Progress monitoring
    - Resume capability detection
    """

    def __init__(self, card_id: str, verbose: bool=True) -> None:
        """
        Initialize checkpoint integration

        Args:
            card_id: Kanban card ID
            verbose: Enable verbose logging
        """
        self.card_id = card_id
        self.verbose = verbose
        self.checkpoint_manager = self._initialize_checkpoint_manager()

    def _initialize_checkpoint_manager(self) -> Optional[Any]:
        """Initialize checkpoint manager"""
        try:
            from checkpoint_manager import CheckpointManager
            return CheckpointManager(card_id=self.card_id, verbose=self.verbose)
        except ImportError:
            if self.verbose:
                
                logger.log(f'[CheckpointIntegration] ⚠️  CheckpointManager not available', 'INFO')
            return None

    def create_checkpoint(self, total_stages: int, execution_context: Dict[str, Any]) -> None:
        """
        Create checkpoint for pipeline execution

        Args:
            total_stages: Total number of stages
            execution_context: Execution context to save
        """
        if not self.checkpoint_manager:
            return
        self.checkpoint_manager.create_checkpoint(total_stages=total_stages, execution_context=execution_context)

    def save_stage_checkpoint(self, stage_name: str, status: str, result: Optional[Dict[str, Any]]=None, start_time: Optional[datetime]=None, end_time: Optional[datetime]=None) -> None:
        """
        Save checkpoint after stage completion

        Args:
            stage_name: Stage name
            status: Stage status (completed, failed, skipped)
            result: Stage result
            start_time: Stage start time
            end_time: Stage end time
        """
        if not self.checkpoint_manager:
            return
        self.checkpoint_manager.save_stage_checkpoint(stage_name=stage_name, status=status, result=result, start_time=start_time, end_time=end_time)

    def can_resume(self) -> bool:
        """
        Check if pipeline can be resumed from checkpoint

        Returns:
            True if checkpoint exists
        """
        if not self.checkpoint_manager:
            return False
        return self.checkpoint_manager.can_resume()

    def resume_from_checkpoint(self) -> Optional[Any]:
        """
        Resume pipeline from checkpoint

        Returns:
            Checkpoint data if available
        """
        if not self.checkpoint_manager:
            return None
        return self.checkpoint_manager.resume()

    def get_progress(self) -> Dict[str, Any]:
        """
        Get checkpoint execution progress

        Returns:
            Progress statistics
        """
        if not self.checkpoint_manager:
            return {'progress_percent': 0, 'stages_completed': 0, 'total_stages': 0}
        return self.checkpoint_manager.get_progress()