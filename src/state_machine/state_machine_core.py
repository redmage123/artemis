from artemis_logger import get_logger
logger = get_logger('state_machine_core')
'\nWHY: Orchestrate all state machine components into cohesive state management system\nRESPONSIBILITY: Facade coordinating transitions, workflows, persistence, and recovery\nPATTERNS: Facade pattern, dependency injection, composition over inheritance\n'
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from state_machine.pipeline_state import PipelineState
from state_machine.stage_state import StageState
from state_machine.event_type import EventType
from state_machine.issue_type import IssueType
from state_machine.pipeline_snapshot import PipelineSnapshot
from state_machine.state_transition_engine import StateTransitionEngine
from state_machine.workflow_executor import WorkflowExecutor
from state_machine.llm_workflow_generator import LLMWorkflowGenerator
from state_machine.pushdown_automaton import PushdownAutomaton
from state_machine.checkpoint_integration import CheckpointIntegration
from state_machine.state_persistence import StatePersistence
from state_machine.stage_state_manager import StageStateManager

class ArtemisStateMachineCore:
    """
    Core state machine orchestrating pipeline lifecycle

    This is the main facade that coordinates:
    - State transitions with validation
    - Workflow execution and recovery
    - State persistence
    - Pushdown automaton for rollback
    - Checkpoint/resume integration
    - Issue tracking and health monitoring

    Features:
    - Complete state tracking for pipeline and stages
    - Event-driven state transitions
    - State history and audit trail
    - Workflow orchestration for issue recovery
    - Snapshot/restore for debugging
    """

    def __init__(self, card_id: str, state_dir: Optional[str]=None, verbose: bool=True, llm_client: Optional[Any]=None):
        """
        Initialize state machine

        Args:
            card_id: Kanban card ID
            state_dir: Directory for state persistence
            verbose: Enable verbose logging
            llm_client: LLM client for dynamic workflow generation
        """
        self.card_id = card_id
        self.llm_client = llm_client
        self.verbose = verbose
        state_dir = state_dir or os.getenv('ARTEMIS_STATE_DIR', '../../.artemis_data/state')
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True, parents=True)
        self.transition_engine = StateTransitionEngine(verbose=verbose)
        self.stage_manager = StageStateManager(verbose=verbose)
        self.automaton = PushdownAutomaton(verbose=verbose)
        self.checkpoint = CheckpointIntegration(card_id=card_id, verbose=verbose)
        self.persistence = StatePersistence(state_dir=self.state_dir, card_id=card_id, verbose=verbose)
        self.workflows = self._register_default_workflows()
        self.workflow_executor = WorkflowExecutor(workflows=self.workflows, verbose=verbose)
        self.llm_generator = LLMWorkflowGenerator(llm_client=llm_client, verbose=verbose)
        if self.verbose:
            
            logger.log(f'[StateMachine] Initialized for card {card_id}', 'INFO')
            
            logger.log(f'[StateMachine] State persistence: {self.state_dir}', 'INFO')

    def _register_default_workflows(self) -> Dict[IssueType, Any]:
        """Register default recovery workflows"""
        try:
            from artemis_workflows import WorkflowBuilder
            workflows = WorkflowBuilder.build_all_workflows()
            if self.verbose:
                
                logger.log(f'[StateMachine] Registered {len(workflows)} recovery workflows', 'INFO')
            return workflows
        except ImportError:
            if self.verbose:
                
                logger.log(f'[StateMachine] ⚠️  WorkflowBuilder not available', 'INFO')
            return {}

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
        success = self.transition_engine.transition(to_state, event, reason, **metadata)
        if success:
            self._save_state()
        return success

    @property
    def current_state(self) -> PipelineState:
        """Get current pipeline state"""
        return self.transition_engine.get_current_state()

    @property
    def state_history(self) -> List[Any]:
        """Get state transition history"""
        return self.transition_engine.get_history()

    def update_stage_state(self, stage_name: str, state: StageState, **metadata) -> None:
        """
        Update state of a specific stage

        Args:
            stage_name: Stage name
            state: New stage state
            **metadata: Additional metadata
        """
        self.stage_manager.update_stage_state(stage_name, state, **metadata)
        self._save_state()

    @property
    def stage_states(self) -> Dict[str, Any]:
        """Get all stage states"""
        return self.stage_manager.get_all_stages()

    @property
    def active_stage(self) -> Optional[str]:
        """Get currently active stage"""
        return self.stage_manager.get_active_stage()

    @active_stage.setter
    def active_stage(self, stage_name: Optional[str]) -> None:
        """Set currently active stage"""
        self.stage_manager.set_active_stage(stage_name)

    def register_issue(self, issue_type: IssueType, **metadata) -> None:
        """
        Register an active issue

        Args:
            issue_type: Type of issue
            **metadata: Issue details
        """
        self.workflow_executor.register_issue(issue_type, **metadata)
        health_status = self.workflow_executor.compute_health_status()
        self._update_health_state(health_status)

    def resolve_issue(self, issue_type: IssueType) -> None:
        """
        Mark an issue as resolved

        Args:
            issue_type: Type of issue
        """
        self.workflow_executor.resolve_issue(issue_type)
        health_status = self.workflow_executor.compute_health_status()
        self._update_health_state(health_status)

    def execute_workflow(self, issue_type: IssueType, context: Optional[Dict[str, Any]]=None) -> bool:
        """
        Execute recovery workflow for an issue

        Args:
            issue_type: Type of issue to handle
            context: Context for workflow execution

        Returns:
            True if workflow succeeded
        """
        success = self.workflow_executor.execute_workflow(issue_type, context)
        if success:
            self._handle_workflow_success(issue_type)
            return True
        generated_workflow = self.llm_generator.generate_workflow(issue_type, context or {})
        if not generated_workflow:
            self._handle_workflow_failure(issue_type)
            return False
        self.workflows[issue_type] = generated_workflow
        self.workflow_executor.workflows = self.workflows
        success = self.workflow_executor.execute_workflow(issue_type, context)
        if success:
            self._handle_workflow_success(issue_type)
        else:
            self._handle_workflow_failure(issue_type)
        return success

    def _update_health_state(self, health_status: str) -> None:
        """Update health state based on status"""
        HEALTH_STATE_MAP = {'critical': (PipelineState.CRITICAL, EventType.HEALTH_CRITICAL), 'degraded': (PipelineState.DEGRADED_HEALTH, EventType.HEALTH_DEGRADED), 'healthy': (PipelineState.HEALTHY, EventType.HEALTH_RESTORED)}
        state_event = HEALTH_STATE_MAP.get(health_status)
        if state_event:
            state, event = state_event
            issue_count = len(self.workflow_executor.active_issues)
            self.transition(state, event, reason=f'{issue_count} active issues')

    def _handle_workflow_success(self, issue_type: IssueType) -> None:
        """Handle successful workflow completion"""
        workflow = self.workflows.get(issue_type)
        if workflow:
            self.transition(workflow.success_state, EventType.RECOVERY_SUCCESS, reason=f'Workflow {workflow.name} completed successfully')

    def _handle_workflow_failure(self, issue_type: IssueType) -> None:
        """Handle workflow failure"""
        workflow = self.workflows.get(issue_type)
        if workflow:
            self.transition(workflow.failure_state, EventType.RECOVERY_FAIL, reason=f'Workflow {workflow.name} failed')

    @property
    def active_issues(self) -> Set[IssueType]:
        """Get active issues"""
        return self.workflow_executor.active_issues

    @property
    def resolved_issues(self) -> List[IssueType]:
        """Get resolved issues"""
        return self.workflow_executor.resolved_issues

    @property
    def workflow_history(self) -> List[Any]:
        """Get workflow execution history"""
        return self.workflow_executor.workflow_history

    def push_state(self, state: PipelineState, context: Optional[Dict[str, Any]]=None) -> None:
        """Push state onto stack for rollback support"""
        self.automaton.push_state(state, context)

    def pop_state(self) -> Optional[Dict[str, Any]]:
        """Pop state from stack"""
        return self.automaton.pop_state()

    def peek_state(self) -> Optional[Dict[str, Any]]:
        """Peek at top of state stack"""
        return self.automaton.peek_state()

    def rollback_to_state(self, target_state: PipelineState) -> bool:
        """
        Rollback to a previous state

        Args:
            target_state: State to rollback to

        Returns:
            True if rollback succeeded
        """
        rollback_steps = self.automaton.rollback_to_state(target_state)
        if not rollback_steps:
            return False
        self.transition(target_state, EventType.ROLLBACK_COMPLETE, reason=f'Rolled back {len(rollback_steps)} states')
        return True

    def get_state_depth(self) -> int:
        """Get current depth of state stack"""
        return self.automaton.get_depth()

    def create_checkpoint(self, total_stages: int) -> None:
        """Create checkpoint for pipeline execution"""
        self.checkpoint.create_checkpoint(total_stages=total_stages, execution_context={'card_id': self.card_id, 'current_state': self.current_state.value})

    def save_stage_checkpoint(self, stage_name: str, status: str, result: Optional[Dict[str, Any]]=None, start_time: Optional[datetime]=None, end_time: Optional[datetime]=None) -> None:
        """Save checkpoint after stage completion"""
        self.checkpoint.save_stage_checkpoint(stage_name=stage_name, status=status, result=result, start_time=start_time, end_time=end_time)

    def can_resume(self) -> bool:
        """Check if pipeline can be resumed from checkpoint"""
        return self.checkpoint.can_resume()

    def resume_from_checkpoint(self) -> Optional[Any]:
        """Resume pipeline from checkpoint"""
        return self.checkpoint.resume_from_checkpoint()

    def get_checkpoint_progress(self) -> Dict[str, Any]:
        """Get checkpoint execution progress"""
        return self.checkpoint.get_progress()

    def get_snapshot(self) -> PipelineSnapshot:
        """Get current pipeline state snapshot"""
        return PipelineSnapshot(state=self.current_state, timestamp=datetime.now(), card_id=self.card_id, stages=self.stage_states, active_stage=self.active_stage, health_status=self.workflow_executor.compute_health_status(), circuit_breakers_open=self.stage_manager.get_circuit_breakers_open(), active_issues=list(self.active_issues))

    def _save_state(self) -> None:
        """Persist state to disk"""
        snapshot = self.get_snapshot()
        self.persistence.save_snapshot(snapshot)

    @property
    def stats(self) -> Dict[str, int]:
        """Get combined statistics from all components"""
        transition_stats = self.transition_engine.get_stats()
        workflow_stats = self.workflow_executor.get_stats()
        return {**transition_stats, **workflow_stats}