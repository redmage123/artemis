#!/usr/bin/env python3
"""
WHY: Provide backward compatibility wrapper for existing code using ArtemisStateMachine
RESPONSIBILITY: Delegate all operations to ArtemisStateMachineCore while maintaining API
PATTERNS: Adapter pattern, delegation pattern, facade pattern
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Set

from state_machine.pipeline_state import PipelineState
from state_machine.stage_state import StageState
from state_machine.event_type import EventType
from state_machine.issue_type import IssueType
from state_machine.state_transition import StateTransition
from state_machine.workflow_execution import WorkflowExecution
from state_machine.pipeline_snapshot import PipelineSnapshot
from state_machine.workflow import Workflow
from state_machine.state_machine_core import ArtemisStateMachineCore


class ArtemisStateMachine:
    """
    Backward compatibility wrapper for ArtemisStateMachine

    This class delegates all operations to ArtemisStateMachineCore while
    maintaining the exact same API as the original 961-line implementation.

    Features:
    - Complete API compatibility
    - Zero breaking changes
    - All original functionality preserved
    - Clean delegation to modular architecture
    """

    def __init__(
        self,
        card_id: str,
        state_dir: Optional[str] = None,
        verbose: bool = True,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize state machine (delegates to core)

        Args:
            card_id: Kanban card ID
            state_dir: Directory for state persistence
            verbose: Enable verbose logging
            llm_client: LLM client for dynamic workflow generation
        """
        self._core = ArtemisStateMachineCore(
            card_id=card_id,
            state_dir=state_dir,
            verbose=verbose,
            llm_client=llm_client
        )

        # Expose properties for backward compatibility
        self.card_id = card_id
        self.llm_client = llm_client
        self.state_dir = self._core.state_dir
        self.verbose = verbose

    # ========================================================================
    # PROPERTY DELEGATION
    # ========================================================================

    @property
    def current_state(self) -> PipelineState:
        """Get current pipeline state"""
        return self._core.current_state

    @property
    def stage_states(self) -> Dict[str, Any]:
        """Get all stage states"""
        return self._core.stage_states

    @property
    def active_stage(self) -> Optional[str]:
        """Get currently active stage"""
        return self._core.active_stage

    @active_stage.setter
    def active_stage(self, value: Optional[str]) -> None:
        """Set currently active stage"""
        self._core.active_stage = value

    @property
    def state_history(self) -> List[StateTransition]:
        """Get state transition history"""
        return self._core.state_history

    @property
    def workflow_history(self) -> List[WorkflowExecution]:
        """Get workflow execution history"""
        return self._core.workflow_history

    @property
    def active_issues(self) -> Set[IssueType]:
        """Get active issues"""
        return self._core.active_issues

    @property
    def resolved_issues(self) -> List[IssueType]:
        """Get resolved issues"""
        return self._core.resolved_issues

    @property
    def workflows(self) -> Dict[IssueType, Workflow]:
        """Get workflows registry"""
        return self._core.workflows

    @property
    def transition_rules(self) -> Dict[PipelineState, Set[PipelineState]]:
        """Get transition rules"""
        return self._core.transition_engine.validator.transition_rules

    @property
    def stats(self) -> Dict[str, int]:
        """Get statistics"""
        return self._core.stats

    # ========================================================================
    # METHOD DELEGATION
    # ========================================================================

    def transition(
        self,
        to_state: PipelineState,
        event: EventType,
        reason: Optional[str] = None,
        **metadata
    ) -> bool:
        """Transition to a new state"""
        return self._core.transition(to_state, event, reason, **metadata)

    def update_stage_state(
        self,
        stage_name: str,
        state: StageState,
        **metadata
    ) -> None:
        """Update state of a specific stage"""
        self._core.update_stage_state(stage_name, state, **metadata)

    def register_issue(self, issue_type: IssueType, **metadata) -> None:
        """Register an active issue"""
        self._core.register_issue(issue_type, **metadata)

    def resolve_issue(self, issue_type: IssueType) -> None:
        """Mark an issue as resolved"""
        self._core.resolve_issue(issue_type)

    def execute_workflow(
        self,
        issue_type: IssueType,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Execute recovery workflow for an issue"""
        return self._core.execute_workflow(issue_type, context)

    def get_snapshot(self) -> PipelineSnapshot:
        """Get current pipeline state snapshot"""
        return self._core.get_snapshot()

    # Pushdown automaton methods
    def push_state(self, state: PipelineState, context: Optional[Dict[str, Any]] = None) -> None:
        """Push state onto stack"""
        self._core.push_state(state, context)

    def pop_state(self) -> Optional[Dict[str, Any]]:
        """Pop state from stack"""
        return self._core.pop_state()

    def peek_state(self) -> Optional[Dict[str, Any]]:
        """Peek at top of state stack"""
        return self._core.peek_state()

    def rollback_to_state(self, target_state: PipelineState) -> bool:
        """Rollback to a previous state"""
        return self._core.rollback_to_state(target_state)

    def get_state_depth(self) -> int:
        """Get current depth of state stack"""
        return self._core.get_state_depth()

    # Checkpoint methods
    def create_checkpoint(self, total_stages: int) -> None:
        """Create checkpoint for pipeline execution"""
        self._core.create_checkpoint(total_stages)

    def save_stage_checkpoint(
        self,
        stage_name: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> None:
        """Save checkpoint after stage completion"""
        self._core.save_stage_checkpoint(stage_name, status, result, start_time, end_time)

    def can_resume(self) -> bool:
        """Check if pipeline can be resumed from checkpoint"""
        return self._core.can_resume()

    def resume_from_checkpoint(self) -> Optional[Any]:
        """Resume pipeline from checkpoint"""
        return self._core.resume_from_checkpoint()

    def get_checkpoint_progress(self) -> Dict[str, Any]:
        """Get checkpoint execution progress"""
        return self._core.get_checkpoint_progress()

    # Private methods for internal use (maintained for compatibility)
    def _build_transition_rules(self) -> Dict[PipelineState, Set[PipelineState]]:
        """Build valid state transition rules (compatibility)"""
        return self.transition_rules

    def _save_state(self) -> None:
        """Persist state to disk (compatibility)"""
        self._core._save_state()

    def _register_default_workflows(self) -> None:
        """Register default recovery workflows (compatibility)"""
        pass  # Already done in core initialization

    def _compute_health_status(self) -> str:
        """Compute current health status (compatibility)"""
        return self._core.workflow_executor.compute_health_status()
