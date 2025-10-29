from artemis_logger import get_logger
logger = get_logger('pattern_recognition')
'\nWHY: Detect unexpected states and assess their severity\nRESPONSIBILITY: Pattern matching for state validation and severity classification\nPATTERNS: Strategy (severity assessment), Guard Clause (state validation)\n'
from typing import Dict, List, Optional, Any
from datetime import datetime
from .models import UnexpectedState

class StatePatternRecognizer:
    """
    WHY: Identify when system enters unexpected states
    RESPONSIBILITY: Compare actual vs expected states and classify anomalies
    PATTERNS: Guard Clause, Strategy (severity assessment)
    """

    def __init__(self, verbose: bool=True):
        self.verbose = verbose
        self.detection_count = 0

    def detect_unexpected_state(self, card_id: str, current_state: str, expected_states: List[str], context: Dict[str, Any]) -> Optional[UnexpectedState]:
        """
        WHY: Identify state transitions that violate expected patterns
        RESPONSIBILITY: Create UnexpectedState object when state is anomalous
        PATTERNS: Guard Clause (early return for expected states)

        Args:
            card_id: Card ID
            current_state: Current pipeline state
            expected_states: List of expected states
            context: Context information

        Returns:
            UnexpectedState if state is unexpected, None otherwise
        """
        if current_state in expected_states:
            return None
        self.detection_count += 1
        unexpected = UnexpectedState(state_id=f'unexpected-{card_id}-{datetime.utcnow().timestamp()}', timestamp=datetime.utcnow().isoformat() + 'Z', card_id=card_id, stage_name=context.get('stage_name'), error_message=context.get('error_message'), context=context, stack_trace=context.get('stack_trace'), previous_state=context.get('previous_state'), current_state=current_state, expected_states=expected_states, severity=self._assess_severity(current_state, context))
        if self.verbose:
            
            logger.log(f'[Learning] 🚨 Unexpected state detected!', 'INFO')
            
            logger.log(f'[Learning]    Current: {current_state}', 'INFO')
            
            logger.log(f'[Learning]    Expected: {expected_states}', 'INFO')
            
            logger.log(f'[Learning]    Severity: {unexpected.severity}', 'INFO')
        return unexpected

    def _assess_severity(self, current_state: str, context: Dict[str, Any]) -> str:
        """
        WHY: Prioritize recovery efforts based on impact
        RESPONSIBILITY: Classify unexpected states by severity level
        PATTERNS: Dispatch table (severity classification rules)

        Returns:
            Severity level: critical, high, medium, or low
        """
        state_upper = current_state.upper()
        if 'FAILED' in state_upper or 'CRITICAL' in state_upper:
            return 'critical'
        if 'ERROR' in state_upper:
            return 'high'
        if context.get('error_message'):
            return 'medium'
        return 'low'

class ProblemDescriptor:
    """
    WHY: Generate human-readable descriptions of problems
    RESPONSIBILITY: Convert UnexpectedState into clear problem statements
    PATTERNS: Template Method (problem description formatting)
    """

    @staticmethod
    def describe_problem(unexpected_state: UnexpectedState) -> str:
        """
        WHY: Create concise problem descriptions for logging and LLM prompts
        RESPONSIBILITY: Format unexpected state as readable text
        """
        parts = [f'Unexpected state: {unexpected_state.current_state}']
        if unexpected_state.stage_name:
            parts.append(f"in stage '{unexpected_state.stage_name}'")
        if unexpected_state.error_message:
            parts.append(f'- Error: {unexpected_state.error_message}')
        return ' '.join(parts)