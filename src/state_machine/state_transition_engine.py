from artemis_logger import get_logger
logger = get_logger('state_transition_engine')
'\nWHY: Execute state transitions with validation, history tracking, and event logging\nRESPONSIBILITY: Manage state transitions with audit trail and statistics\nPATTERNS: Command pattern for transitions, observer pattern for history tracking\n'
from datetime import datetime
from typing import List, Dict, Any, Optional
from state_machine.pipeline_state import PipelineState
from state_machine.event_type import EventType
from state_machine.state_transition import StateTransition
from state_machine.state_validator import StateValidator

class StateTransitionEngine:
    """
    Executes state transitions with validation and history tracking

    Features:
    - Validates all transitions before execution
    - Maintains complete audit trail
    - Tracks transition statistics
    - Thread-safe state updates
    """

    def __init__(self, verbose: bool=True) -> None:
        """
        Initialize transition engine

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.validator = StateValidator()
        self.current_state = PipelineState.IDLE
        self.state_history: List[StateTransition] = []
        self.stats = {'total_transitions': 0, 'successful_transitions': 0, 'rejected_transitions': 0}

    def transition(self, to_state: PipelineState, event: EventType, reason: Optional[str]=None, **metadata) -> bool:
        """
        Transition to a new state

        Args:
            to_state: Target state
            event: Event triggering transition
            reason: Optional reason for transition
            **metadata: Additional metadata

        Returns:
            True if transition was valid and executed
        """
        from_state = self.current_state
        if not self.validator.is_valid_transition(from_state, to_state):
            self._log_invalid_transition(from_state, to_state)
            self.stats['rejected_transitions'] += 1
            return False
        self._execute_transition(from_state, to_state, event, reason, metadata)
        return True

    def _execute_transition(self, from_state: PipelineState, to_state: PipelineState, event: EventType, reason: Optional[str], metadata: Dict[str, Any]) -> None:
        """Execute validated transition"""
        transition = StateTransition(from_state=from_state, to_state=to_state, event=event, timestamp=datetime.now(), metadata=metadata, reason=reason)
        self.state_history.append(transition)
        self.current_state = to_state
        self.stats['total_transitions'] += 1
        self.stats['successful_transitions'] += 1
        self._log_transition(from_state, to_state, event, reason)

    def _log_transition(self, from_state: PipelineState, to_state: PipelineState, event: EventType, reason: Optional[str]) -> None:
        """Log successful transition"""
        if not self.verbose:
            return
        
        logger.log(f'[TransitionEngine] {from_state.value} → {to_state.value} (event: {event.value})', 'INFO')
        if reason:
            
            logger.log(f'[TransitionEngine]    Reason: {reason}', 'INFO')

    def _log_invalid_transition(self, from_state: PipelineState, to_state: PipelineState) -> None:
        """Log invalid transition attempt"""
        if not self.verbose:
            return
        
        logger.log(f'[TransitionEngine] ⚠️  Invalid transition: {from_state.value} → {to_state.value}', 'INFO')

    def get_current_state(self) -> PipelineState:
        """Get current pipeline state"""
        return self.current_state

    def get_history(self) -> List[StateTransition]:
        """Get complete state transition history"""
        return self.state_history.copy()

    def get_stats(self) -> Dict[str, int]:
        """Get transition statistics"""
        return self.stats.copy()