#!/usr/bin/env python3
"""
WHY: Execute recovery workflows with retry, rollback, and issue tracking
RESPONSIBILITY: Orchestrate workflow execution, handle failures, track issues
PATTERNS: Command pattern for actions, template method for execution flow
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Set, List

from artemis_constants import RETRY_BACKOFF_FACTOR
from state_machine.issue_type import IssueType
from state_machine.pipeline_state import PipelineState
from state_machine.event_type import EventType
from state_machine.workflow import Workflow
from state_machine.workflow_action import WorkflowAction
from state_machine.workflow_execution import WorkflowExecution


class WorkflowExecutor:
    """
    Executes recovery workflows with retry and rollback support

    Features:
    - Sequential action execution with retry
    - Automatic rollback on failure
    - Issue tracking and resolution
    - Health status monitoring
    """

    def __init__(
        self,
        workflows: Dict[IssueType, Workflow],
        verbose: bool = True
    ) -> None:
        """
        Initialize workflow executor

        Args:
            workflows: Registry of workflows by issue type
            verbose: Enable verbose logging
        """
        self.workflows = workflows
        self.verbose = verbose
        self.workflow_history: List[WorkflowExecution] = []
        self.active_issues: Set[IssueType] = set()
        self.resolved_issues: List[IssueType] = []
        self.stats = {
            "workflow_executions": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "issues_resolved": 0
        }

    def register_issue(self, issue_type: IssueType, **metadata) -> None:
        """
        Register an active issue

        Args:
            issue_type: Type of issue
            **metadata: Issue details
        """
        self.active_issues.add(issue_type)

        if self.verbose:
            print(f"[WorkflowExecutor] 🚨 Issue registered: {issue_type.value}")

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
            print(f"[WorkflowExecutor] ✅ Issue resolved: {issue_type.value}")

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
        # Guard: Check workflow exists
        workflow = self.workflows.get(issue_type)
        if not workflow:
            self._log_missing_workflow(issue_type)
            return False

        execution = self._create_execution_record(workflow, issue_type)
        self.stats["workflow_executions"] += 1

        if self.verbose:
            print(f"[WorkflowExecutor] 🔧 Executing workflow: {workflow.name}")

        try:
            return self._execute_workflow_actions(workflow, execution, context or {})
        except Exception as e:
            return self._handle_workflow_exception(execution, workflow, e)

    def _execute_workflow_actions(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        context: Dict[str, Any]
    ) -> bool:
        """Execute all workflow actions in sequence"""
        for action in workflow.actions:
            if self.verbose:
                print(f"[WorkflowExecutor]    Action: {action.action_name}")

            success = self._execute_action(action, context)
            execution.actions_taken.append(action.action_name)

            if not success:
                return self._handle_action_failure(execution, workflow, action)

        # All actions succeeded
        return self._complete_workflow_successfully(execution, workflow)

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
            success = self._attempt_action(action, context, attempt, max_attempts)
            if success:
                return True

            # Guard: No more retries
            should_retry = action.retry_on_failure and attempt < max_attempts - 1
            if not should_retry:
                return False

            time.sleep(RETRY_BACKOFF_FACTOR ** attempt)

        return False

    def _attempt_action(
        self,
        action: WorkflowAction,
        context: Dict[str, Any],
        attempt: int,
        max_attempts: int
    ) -> bool:
        """Attempt action execution"""
        try:
            result = action.handler(context)
            if result:
                return True

            # Log retry if needed
            should_retry = action.retry_on_failure and attempt < max_attempts - 1
            if should_retry and self.verbose:
                print(f"[WorkflowExecutor]       Retry {attempt + 1}/{action.max_retries}")

            return False

        except Exception as e:
            if self.verbose:
                print(f"[WorkflowExecutor]       Error: {e}")
            return False

    def _handle_action_failure(
        self,
        execution: WorkflowExecution,
        workflow: Workflow,
        action: WorkflowAction
    ) -> bool:
        """Handle failure of a workflow action"""
        if workflow.rollback_on_failure:
            self._rollback_workflow(execution, workflow)

        execution.success = False
        execution.end_time = datetime.now()
        self.workflow_history.append(execution)
        self.stats["failed_recoveries"] += 1

        return False

    def _complete_workflow_successfully(
        self,
        execution: WorkflowExecution,
        workflow: Workflow
    ) -> bool:
        """Complete workflow successfully"""
        execution.success = True
        execution.end_time = datetime.now()
        self.workflow_history.append(execution)
        self.stats["successful_recoveries"] += 1

        # Resolve issue
        self.resolve_issue(workflow.issue_type)

        if self.verbose:
            print(f"[WorkflowExecutor] ✅ Workflow completed: {workflow.name}")

        return True

    def _handle_workflow_exception(
        self,
        execution: WorkflowExecution,
        workflow: Workflow,
        error: Exception
    ) -> bool:
        """Handle workflow execution exception"""
        if self.verbose:
            print(f"[WorkflowExecutor] ❌ Workflow error: {error}")

        execution.success = False
        execution.end_time = datetime.now()
        execution.metadata["error"] = str(error)
        self.workflow_history.append(execution)
        self.stats["failed_recoveries"] += 1

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
            print(f"[WorkflowExecutor] 🔄 Rolling back workflow: {workflow.name}")

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
                print(f"[WorkflowExecutor]    Rolled back: {action_name}")
        except Exception as e:
            if self.verbose:
                print(f"[WorkflowExecutor]    Rollback failed for {action_name}: {e}")

    def _create_execution_record(
        self,
        workflow: Workflow,
        issue_type: IssueType
    ) -> WorkflowExecution:
        """Create workflow execution record"""
        return WorkflowExecution(
            workflow_name=workflow.name,
            issue_type=issue_type,
            start_time=datetime.now()
        )

    def _log_missing_workflow(self, issue_type: IssueType) -> None:
        """Log missing workflow warning"""
        if self.verbose:
            print(f"[WorkflowExecutor] ⚠️  No workflow registered for {issue_type.value}")

    def compute_health_status(self) -> str:
        """Compute current health status based on active issues"""
        issue_count = len(self.active_issues)

        if issue_count >= 3:
            return "critical"
        if issue_count >= 1:
            return "degraded"
        return "healthy"

    def get_stats(self) -> Dict[str, int]:
        """Get workflow execution statistics"""
        return self.stats.copy()
