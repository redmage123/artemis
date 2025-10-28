#!/usr/bin/env python3
"""
WHY: Manage complete pipeline state tracking with event-driven transitions and recovery workflows
RESPONSIBILITY: Central state machine orchestrating pipeline lifecycle, transitions, and recovery
PATTERNS: State machine, event-driven architecture, workflow orchestration, pushdown automaton
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

from artemis_constants import RETRY_BACKOFF_FACTOR
from state_machine.pipeline_state import PipelineState
from state_machine.stage_state import StageState
from state_machine.event_type import EventType
from state_machine.issue_type import IssueType
from state_machine.state_transition import StateTransition
from state_machine.stage_state_info import StageStateInfo
from state_machine.workflow_execution import WorkflowExecution
from state_machine.pipeline_snapshot import PipelineSnapshot
from state_machine.workflow_action import WorkflowAction
from state_machine.workflow import Workflow


class ArtemisStateMachine:
    """
    State machine for tracking Artemis pipeline execution

    Features:
    - Complete state tracking for pipeline and all stages
    - Event-driven state transitions
    - State history and audit trail
    - Workflow orchestration for issue recovery
    - Snapshot/restore for debugging
    """

    def __init__(
        self,
        card_id: str,
        state_dir: Optional[str] = None,
        verbose: bool = True,
        llm_client: Optional[Any] = None
    ):
        """
        Initialize state machine

        Args:
            card_id: Kanban card ID
            state_dir: Directory for state persistence (defaults to env var or repo path)
            verbose: Enable verbose logging
            llm_client: LLM client for dynamic workflow generation
        """
        import os
        self.card_id = card_id
        self.llm_client = llm_client

        # Get state dir from parameter, env var, or default
        state_dir = state_dir or os.getenv("ARTEMIS_STATE_DIR", "../../.artemis_data/state")

        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True, parents=True)
        self.verbose = verbose

        # Current state
        self.current_state = PipelineState.IDLE
        self.stage_states: Dict[str, StageStateInfo] = {}
        self.active_stage: Optional[str] = None

        # State history
        self.state_history: List[StateTransition] = []
        self.workflow_history: List[WorkflowExecution] = []

        # Issue tracking
        self.active_issues: Set[IssueType] = set()
        self.resolved_issues: List[IssueType] = []

        # Workflows registry
        self.workflows: Dict[IssueType, Workflow] = {}
        self._register_default_workflows()

        # Transition rules
        self.transition_rules = self._build_transition_rules()

        # Statistics
        self.stats = {
            "total_transitions": 0,
            "workflow_executions": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "issues_resolved": 0
        }

        if self.verbose:
            print(f"[StateMachine] Initialized for card {card_id}")
            print(f"[StateMachine] State persistence: {self.state_dir}")

    def _build_transition_rules(self) -> Dict[PipelineState, Set[PipelineState]]:
        """
        Build valid state transition rules

        Returns:
            Map of state → valid next states
        """
        return {
            PipelineState.IDLE: {
                PipelineState.INITIALIZING,
                PipelineState.ABORTED
            },
            PipelineState.INITIALIZING: {
                PipelineState.RUNNING,
                PipelineState.FAILED,
                PipelineState.ABORTED
            },
            PipelineState.RUNNING: {
                PipelineState.STAGE_RUNNING,
                PipelineState.PAUSED,
                PipelineState.COMPLETED,
                PipelineState.FAILED,
                PipelineState.DEGRADED,
                PipelineState.ABORTED
            },
            PipelineState.STAGE_RUNNING: {
                PipelineState.STAGE_COMPLETED,
                PipelineState.STAGE_FAILED,
                PipelineState.STAGE_RETRYING,
                PipelineState.STAGE_SKIPPED,
                PipelineState.RUNNING
            },
            PipelineState.STAGE_FAILED: {
                PipelineState.STAGE_RETRYING,
                PipelineState.RECOVERING,
                PipelineState.FAILED,
                PipelineState.ROLLING_BACK
            },
            PipelineState.RECOVERING: {
                PipelineState.RUNNING,
                PipelineState.DEGRADED,
                PipelineState.FAILED,
                PipelineState.ROLLING_BACK
            },
            PipelineState.DEGRADED: {
                PipelineState.RUNNING,
                PipelineState.COMPLETED,
                PipelineState.FAILED
            },
            PipelineState.PAUSED: {
                PipelineState.RUNNING,
                PipelineState.ABORTED
            },
            PipelineState.ROLLING_BACK: {
                PipelineState.FAILED,
                PipelineState.ABORTED
            },
            PipelineState.FAILED: {
                PipelineState.RECOVERING,
                PipelineState.ROLLING_BACK,
                PipelineState.ABORTED
            },
            # Terminal states
            PipelineState.COMPLETED: set(),
            PipelineState.ABORTED: set()
        }

    def transition(
        self,
        to_state: PipelineState,
        event: EventType,
        reason: Optional[str] = None,
        **metadata
    ) -> bool:
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

        # Check if transition is valid
        valid_next_states = self.transition_rules.get(from_state, set())
        if to_state not in valid_next_states and to_state != from_state:
            if self.verbose:
                print(f"[StateMachine] ⚠️  Invalid transition: {from_state.value} → {to_state.value}")
            return False

        # Execute transition
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            event=event,
            timestamp=datetime.now(),
            metadata=metadata,
            reason=reason
        )

        self.state_history.append(transition)
        self.current_state = to_state
        self.stats["total_transitions"] += 1

        if self.verbose:
            print(f"[StateMachine] {from_state.value} → {to_state.value} (event: {event.value})")
            if reason:
                print(f"[StateMachine]    Reason: {reason}")

        # Persist state
        self._save_state()

        return True

    def update_stage_state(
        self,
        stage_name: str,
        state: StageState,
        **metadata
    ) -> None:
        """
        Update state of a specific stage

        Args:
            stage_name: Stage name
            state: New stage state
            **metadata: Additional metadata
        """
        if stage_name not in self.stage_states:
            self.stage_states[stage_name] = StageStateInfo(
                stage_name=stage_name,
                state=state,
                start_time=datetime.now()
            )
        else:
            self._update_existing_stage_state(stage_name, state)

        # Update metadata
        self.stage_states[stage_name].metadata.update(metadata)

        if self.verbose:
            print(f"[StateMachine] Stage '{stage_name}' → {state.value}")

        self._save_state()

    def _update_existing_stage_state(self, stage_name: str, state: StageState) -> None:
        """Update state for an existing stage"""
        stage_info = self.stage_states[stage_name]
        stage_info.state = state

        is_terminal_state = state == StageState.COMPLETED or state == StageState.FAILED
        if not is_terminal_state:
            return

        stage_info.end_time = datetime.now()
        if not stage_info.start_time:
            return

        stage_info.duration_seconds = (
            stage_info.end_time - stage_info.start_time
        ).total_seconds()

    def register_issue(self, issue_type: IssueType, **metadata) -> None:
        """
        Register an active issue

        Args:
            issue_type: Type of issue
            **metadata: Issue details
        """
        self.active_issues.add(issue_type)

        if self.verbose:
            print(f"[StateMachine] 🚨 Issue registered: {issue_type.value}")

        # Trigger health degradation if needed
        if len(self.active_issues) >= 3:
            self.transition(
                PipelineState.CRITICAL,
                EventType.HEALTH_CRITICAL,
                reason=f"{len(self.active_issues)} active issues"
            )
        elif len(self.active_issues) >= 1:
            self.transition(
                PipelineState.DEGRADED_HEALTH,
                EventType.HEALTH_DEGRADED,
                reason=f"{len(self.active_issues)} active issues"
            )

    def resolve_issue(self, issue_type: IssueType) -> None:
        """
        Mark an issue as resolved

        Args:
            issue_type: Type of issue
        """
        if issue_type not in self.active_issues:
            return

        self.active_issues.remove(issue_type)
        self.resolved_issues.append(issue_type)
        self.stats["issues_resolved"] += 1

        if self.verbose:
            print(f"[StateMachine] ✅ Issue resolved: {issue_type.value}")

        self._restore_health_if_cleared()

    def _restore_health_if_cleared(self) -> None:
        """Restore health status if all issues are resolved"""
        if len(self.active_issues) != 0:
            return

        self.transition(
            PipelineState.HEALTHY,
            EventType.HEALTH_RESTORED,
            reason="All issues resolved"
        )

    def execute_workflow(
        self,
        issue_type: IssueType,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute recovery workflow for an issue

        Args:
            issue_type: Type of issue to handle
            context: Context for workflow execution

        Returns:
            True if workflow succeeded
        """
        workflow = self._get_or_generate_workflow(issue_type, context or {})
        if not workflow:
            return False

        execution = WorkflowExecution(
            workflow_name=workflow.name,
            issue_type=issue_type,
            start_time=datetime.now()
        )

        self.stats["workflow_executions"] += 1

        if self.verbose:
            print(f"[StateMachine] 🔧 Executing workflow: {workflow.name}")

        try:
            # Execute each action in sequence
            for action in workflow.actions:
                if self.verbose:
                    print(f"[StateMachine]    Action: {action.action_name}")

                # Execute action with retry
                success = self._execute_action(action, context or {})
                execution.actions_taken.append(action.action_name)

                if not success:
                    return self._handle_workflow_action_failure(execution, workflow, action)

            # All actions succeeded
            return self._complete_workflow_successfully(execution, workflow, issue_type)

        except Exception as e:
            if self.verbose:
                print(f"[StateMachine] ❌ Workflow error: {e}")

            execution.success = False
            execution.end_time = datetime.now()
            execution.metadata["error"] = str(e)
            self.workflow_history.append(execution)
            self.stats["failed_recoveries"] += 1

            return False

    def _get_or_generate_workflow(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> Optional[Workflow]:
        """Get existing workflow or generate one with LLM"""
        workflow = self.workflows.get(issue_type)
        if workflow:
            return workflow

        if self.verbose:
            print(f"[StateMachine] ⚠️  No workflow registered for {issue_type.value}")

        # Try to generate workflow using LLM before falling back to failure
        generated_workflow = self._generate_workflow_with_llm(issue_type, context)
        if not generated_workflow:
            return None

        if self.verbose:
            print(f"[StateMachine] ✅ Generated new workflow using LLM: {generated_workflow.name}")

        return generated_workflow

    def _handle_workflow_action_failure(
        self,
        execution: WorkflowExecution,
        workflow: Workflow,
        action: WorkflowAction
    ) -> bool:
        """Handle failure of a workflow action"""
        if workflow.rollback_on_failure:
            if self.verbose:
                print(f"[StateMachine]    Rolling back workflow...")
            self._rollback_workflow(execution, workflow)

        execution.success = False
        execution.end_time = datetime.now()
        self.workflow_history.append(execution)
        self.stats["failed_recoveries"] += 1

        # Transition to failure state
        self.transition(
            workflow.failure_state,
            EventType.RECOVERY_FAIL,
            reason=f"Workflow {workflow.name} failed at action {action.action_name}"
        )

        return False

    def _complete_workflow_successfully(
        self,
        execution: WorkflowExecution,
        workflow: Workflow,
        issue_type: IssueType
    ) -> bool:
        """Complete workflow successfully"""
        execution.success = True
        execution.end_time = datetime.now()
        self.workflow_history.append(execution)
        self.stats["successful_recoveries"] += 1

        # Resolve issue
        self.resolve_issue(issue_type)

        # Transition to success state
        self.transition(
            workflow.success_state,
            EventType.RECOVERY_SUCCESS,
            reason=f"Workflow {workflow.name} completed successfully"
        )

        if self.verbose:
            print(f"[StateMachine] ✅ Workflow completed: {workflow.name}")

        return True

    def _execute_action(
        self,
        action: WorkflowAction,
        context: Dict[str, Any]
    ) -> bool:
        """
        Execute a single workflow action with retry

        Args:
            action: Action to execute
            context: Execution context

        Returns:
            True if action succeeded
        """
        max_attempts = action.max_retries if action.retry_on_failure else 1

        for attempt in range(max_attempts):
            try:
                result = action.handler(context)
                if result:
                    return True

                should_retry = action.retry_on_failure and attempt < max_attempts - 1
                if not should_retry:
                    return False

                if self.verbose:
                    print(f"[StateMachine]       Retry {attempt + 1}/{action.max_retries}")
                time.sleep(RETRY_BACKOFF_FACTOR ** attempt)

            except Exception as e:
                if self.verbose:
                    print(f"[StateMachine]       Error: {e}")

                should_retry = action.retry_on_failure and attempt < max_attempts - 1
                if not should_retry:
                    return False

                time.sleep(RETRY_BACKOFF_FACTOR ** attempt)

        return False

    def _rollback_workflow(
        self,
        execution: WorkflowExecution,
        workflow: Workflow
    ) -> None:
        """
        Rollback a failed workflow

        Args:
            execution: Workflow execution record
            workflow: Workflow definition
        """
        if self.verbose:
            print(f"[StateMachine] 🔄 Rolling back workflow: {workflow.name}")

        # Execute rollback handlers in reverse order
        for action_name in reversed(execution.actions_taken):
            action = next((a for a in workflow.actions if a.action_name == action_name), None)
            self._rollback_single_action(action, action_name)

    def _rollback_single_action(
        self,
        action: Optional[WorkflowAction],
        action_name: str
    ) -> None:
        """Rollback a single action"""
        if not action or not action.rollback_handler:
            return

        try:
            action.rollback_handler({})
            if self.verbose:
                print(f"[StateMachine]    Rolled back: {action_name}")
        except Exception as e:
            if self.verbose:
                print(f"[StateMachine]    Rollback failed for {action_name}: {e}")

    def get_snapshot(self) -> PipelineSnapshot:
        """
        Get current pipeline state snapshot

        Returns:
            Complete pipeline snapshot
        """
        return PipelineSnapshot(
            state=self.current_state,
            timestamp=datetime.now(),
            card_id=self.card_id,
            stages=dict(self.stage_states),
            active_stage=self.active_stage,
            health_status=self._compute_health_status(),
            circuit_breakers_open=[
                name for name, info in self.stage_states.items()
                if info.state == StageState.CIRCUIT_OPEN
            ],
            active_issues=list(self.active_issues)
        )

    def _compute_health_status(self) -> str:
        """Compute current health status"""
        if len(self.active_issues) >= 3:
            return "critical"
        if len(self.active_issues) >= 1:
            return "degraded"
        return "healthy"

    def _save_state(self) -> None:
        """Persist state to disk"""
        snapshot = self.get_snapshot()
        state_file = self.state_dir / f"{self.card_id}_state.json"

        # Convert snapshot to JSON-serializable format
        state_data = {
            "state": snapshot.state.value,
            "timestamp": snapshot.timestamp.isoformat(),
            "card_id": snapshot.card_id,
            "active_stage": snapshot.active_stage,
            "health_status": snapshot.health_status,
            "circuit_breakers_open": snapshot.circuit_breakers_open,
            "active_issues": [issue.value for issue in snapshot.active_issues],
            "stages": {
                name: {
                    "stage_name": info.stage_name,
                    "state": info.state.value,
                    "start_time": info.start_time.isoformat() if info.start_time else None,
                    "end_time": info.end_time.isoformat() if info.end_time else None,
                    "duration_seconds": info.duration_seconds,
                    "retry_count": info.retry_count,
                    "error_message": info.error_message,
                    "metadata": info.metadata
                }
                for name, info in snapshot.stages.items()
            }
        }

        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    def _register_default_workflows(self) -> None:
        """Register default recovery workflows for all issue types"""
        from artemis_workflows import WorkflowBuilder
        from checkpoint_manager import CheckpointManager

        # Register all workflows
        self.workflows = WorkflowBuilder.build_all_workflows()

        # Initialize checkpoint manager
        self.checkpoint_manager = CheckpointManager(
            card_id=self.card_id,
            verbose=self.verbose
        )

        if self.verbose:
            print(f"[StateMachine] Registered {len(self.workflows)} recovery workflows")

    def _generate_workflow_with_llm(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> Optional[Workflow]:
        """
        Generate a recovery workflow using LLM when no registered workflow exists

        Args:
            issue_type: Type of issue needing a workflow
            context: Context about the issue

        Returns:
            Generated Workflow if successful, None otherwise
        """
        if not self.llm_client:
            if self.verbose:
                print(f"[StateMachine] ⚠️  Cannot generate workflow - no LLM client available")
            return None

        if self.verbose:
            print(f"[StateMachine] 🤖 Consulting LLM to generate workflow for {issue_type.value}...")

        try:
            llm_response = self._get_llm_workflow_response(issue_type, context)
            workflow_data = self._parse_llm_workflow_response(llm_response)
            if not workflow_data:
                return None

            workflow = self._build_workflow_from_data(workflow_data, issue_type)

            if self.verbose:
                print(f"[StateMachine] ✅ Generated workflow '{workflow.name}' with {len(workflow.actions)} actions")

            return workflow

        except Exception as e:
            if self.verbose:
                print(f"[StateMachine] ❌ Failed to generate workflow: {e}")
            return None

    def _get_llm_workflow_response(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> str:
        """Get LLM response for workflow generation"""
        system_message = """You are an expert in designing recovery workflows for software pipelines.
When given an issue type and context, you generate a step-by-step recovery workflow in JSON format."""

        context_str = "\n".join(f"- {k}: {v}" for k, v in context.items() if v is not None)

        user_message = f"""Generate a recovery workflow for the following issue:

Issue Type: {issue_type.value}
Context:
{context_str}

Provide a recovery workflow in JSON format:
{{
  "workflow_name": "Brief descriptive name",
  "description": "What this workflow does",
  "actions": [
    {{
      "action_name": "retry_with_backoff",
      "description": "What this action does",
      "max_attempts": 3,
      "parameters": {{"backoff_seconds": 60}}
    }}
  ],
  "success_state": "STAGE_RUNNING",
  "failure_state": "STAGE_FAILED",
  "rollback_on_failure": false
}}

Available actions: retry_with_backoff, reset_state, skip_stage, use_cached_result, fallback_to_default
Available states: IDLE, INITIALIZING, RUNNING, PAUSED, COMPLETED, FAILED, STAGE_RUNNING, STAGE_FAILED"""

        from llm_client import LLMMessage
        messages = [
            LLMMessage(role="system", content=system_message),
            LLMMessage(role="user", content=user_message)
        ]

        llm_response = self.llm_client.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        return llm_response.content

    def _parse_llm_workflow_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON workflow from LLM response"""
        import json
        import re

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            if self.verbose:
                print(f"[StateMachine] ⚠️  LLM response did not contain valid JSON")
            return None

        return json.loads(json_match.group(0))

    def _build_workflow_from_data(
        self,
        workflow_data: Dict[str, Any],
        issue_type: IssueType
    ) -> Workflow:
        """Build Workflow object from parsed data"""
        actions = []
        for action_data in workflow_data.get("actions", []):
            actions.append(WorkflowAction(
                action_name=action_data.get("action_name", "retry_with_backoff"),
                handler=lambda ctx: True,  # Placeholder handler
                max_retries=action_data.get("max_attempts", 1)
            ))

        # Parse states
        success_state_str = workflow_data.get("success_state", "STAGE_RUNNING")
        failure_state_str = workflow_data.get("failure_state", "STAGE_FAILED")

        success_state = (
            PipelineState[success_state_str]
            if success_state_str in PipelineState.__members__
            else PipelineState.RUNNING
        )
        failure_state = (
            PipelineState[failure_state_str]
            if failure_state_str in PipelineState.__members__
            else PipelineState.FAILED
        )

        return Workflow(
            name=workflow_data.get("workflow_name", f"LLM-generated-{issue_type.value}"),
            issue_type=issue_type,
            actions=actions,
            success_state=success_state,
            failure_state=failure_state,
            rollback_on_failure=workflow_data.get("rollback_on_failure", False)
        )

    # ========================================================================
    # PUSHDOWN AUTOMATON FEATURES
    # ========================================================================

    def push_state(self, state: PipelineState, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Push state onto stack (Pushdown Automaton feature)

        Enables backtracking and rollback by maintaining state stack

        Args:
            state: State to push
            context: Optional context for this state
        """
        if not hasattr(self, '_state_stack'):
            self._state_stack = []

        self._state_stack.append({
            "state": state,
            "timestamp": datetime.now(),
            "context": context or {}
        })

        if self.verbose:
            print(f"[StateMachine] Pushed state onto stack: {state.value} (depth: {len(self._state_stack)})")

    def pop_state(self) -> Optional[Dict[str, Any]]:
        """
        Pop state from stack (Pushdown Automaton feature)

        Returns:
            Previous state and context, or None if stack is empty
        """
        if not hasattr(self, '_state_stack') or not self._state_stack:
            return None

        popped = self._state_stack.pop()

        if self.verbose:
            print(f"[StateMachine] Popped state from stack: {popped['state'].value} (depth: {len(self._state_stack)})")

        return popped

    def peek_state(self) -> Optional[Dict[str, Any]]:
        """
        Peek at top of state stack without removing

        Returns:
            Top state and context, or None if stack is empty
        """
        if not hasattr(self, '_state_stack') or not self._state_stack:
            return None

        return self._state_stack[-1]

    def rollback_to_state(self, target_state: PipelineState) -> bool:
        """
        Rollback to a previous state using the state stack

        Args:
            target_state: State to rollback to

        Returns:
            True if rollback succeeded
        """
        if not hasattr(self, '_state_stack'):
            return False

        rollback_steps = self._find_rollback_path(target_state)
        if not rollback_steps:
            if self.verbose:
                print(f"[StateMachine] ⚠️  State {target_state.value} not found in stack")
            return False

        return self._execute_rollback_to_state(target_state, rollback_steps)

    def _find_rollback_path(self, target_state: PipelineState) -> List[Dict[str, Any]]:
        """Find path to rollback to target state"""
        rollback_steps = []
        for i in range(len(self._state_stack) - 1, -1, -1):
            state_info = self._state_stack[i]
            rollback_steps.append(state_info)

            if state_info["state"] == target_state:
                return rollback_steps

        return []

    def _execute_rollback_to_state(
        self,
        target_state: PipelineState,
        rollback_steps: List[Dict[str, Any]]
    ) -> bool:
        """Execute the rollback to target state"""
        if self.verbose:
            print(f"[StateMachine] Rolling back {len(rollback_steps)} states to {target_state.value}")

        # Pop all states until target
        for _ in range(len(rollback_steps) - 1):
            self.pop_state()

        # Transition to target state
        self.transition(
            target_state,
            EventType.ROLLBACK_COMPLETE,
            reason=f"Rolled back {len(rollback_steps)} states"
        )

        return True

    def get_state_depth(self) -> int:
        """
        Get current depth of state stack

        Returns:
            Number of states on stack
        """
        if not hasattr(self, '_state_stack'):
            return 0
        return len(self._state_stack)

    # ========================================================================
    # CHECKPOINT/RESUME INTEGRATION
    # ========================================================================

    def create_checkpoint(self, total_stages: int) -> None:
        """
        Create checkpoint for pipeline execution

        Args:
            total_stages: Total number of stages
        """
        if hasattr(self, 'checkpoint_manager'):
            self.checkpoint_manager.create_checkpoint(
                total_stages=total_stages,
                execution_context={
                    "card_id": self.card_id,
                    "current_state": self.current_state.value
                }
            )

    def save_stage_checkpoint(
        self,
        stage_name: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> None:
        """
        Save checkpoint after stage completion

        Args:
            stage_name: Stage name
            status: Stage status (completed, failed, skipped)
            result: Stage result
            start_time: Stage start time
            end_time: Stage end time
        """
        if hasattr(self, 'checkpoint_manager'):
            self.checkpoint_manager.save_stage_checkpoint(
                stage_name=stage_name,
                status=status,
                result=result,
                start_time=start_time,
                end_time=end_time
            )

    def can_resume(self) -> bool:
        """
        Check if pipeline can be resumed from checkpoint

        Returns:
            True if checkpoint exists
        """
        if hasattr(self, 'checkpoint_manager'):
            return self.checkpoint_manager.can_resume()
        return False

    def resume_from_checkpoint(self) -> Optional[Any]:
        """
        Resume pipeline from checkpoint

        Returns:
            Checkpoint data if available
        """
        if hasattr(self, 'checkpoint_manager'):
            return self.checkpoint_manager.resume()
        return None

    def get_checkpoint_progress(self) -> Dict[str, Any]:
        """
        Get checkpoint execution progress

        Returns:
            Progress statistics
        """
        if hasattr(self, 'checkpoint_manager'):
            return self.checkpoint_manager.get_progress()
        return {
            "progress_percent": 0,
            "stages_completed": 0,
            "total_stages": 0
        }
