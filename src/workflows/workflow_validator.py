#!/usr/bin/env python3
"""
Workflow Validator - Validation and Verification of Workflows

WHAT:
Validates workflow definitions to ensure they are well-formed, complete,
and follow best practices. Catches configuration errors at startup.

WHY:
Invalid workflows cause runtime failures during recovery attempts.
Validation at startup catches errors early when they're easier to debug.

RESPONSIBILITY:
- Validate workflow structure and completeness
- Verify action handlers are callable
- Check workflow metadata consistency
- Validate state transitions are valid

PATTERNS:
- Validator Pattern: Separate validation from workflow logic
- Guard Clauses: Early return on validation failures (no nested ifs)
- Builder Pattern: Accumulate validation errors for complete report

INTEGRATION:
- Used by: WorkflowRegistry at initialization
- Validates: Workflow objects from workflow definitions
- Reports: Detailed validation errors for debugging

EXAMPLE:
    validator = WorkflowValidator()
    result = validator.validate_workflow(workflow)
    if not result.is_valid:
        print(result.errors)
"""

from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass
from state_machine import IssueType, Workflow, WorkflowAction, PipelineState


# ============================================================================
# VALIDATION RESULT
# ============================================================================

@dataclass
class ValidationResult:
    """
    Result of workflow validation

    WHAT:
    Contains validation status and list of any errors found.

    WHY:
    Structured validation results enable detailed error reporting
    and programmatic handling of validation failures.

    ATTRIBUTES:
        is_valid: Whether workflow passed validation
        errors: List of validation error messages
        warnings: List of validation warnings (non-fatal)
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    @staticmethod
    def success() -> 'ValidationResult':
        """Create successful validation result"""
        return ValidationResult(is_valid=True, errors=[], warnings=[])

    @staticmethod
    def failure(errors: List[str], warnings: Optional[List[str]] = None) -> 'ValidationResult':
        """Create failed validation result"""
        return ValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings or []
        )

    def add_error(self, error: str) -> None:
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add validation warning"""
        self.warnings.append(warning)


# ============================================================================
# WORKFLOW VALIDATOR
# ============================================================================

class WorkflowValidator:
    """
    Validates workflow definitions

    WHAT:
    Validates workflows to ensure they are well-formed, complete,
    and follow best practices. Catches configuration errors early.

    WHY:
    Invalid workflows cause runtime failures during recovery.
    Startup validation catches errors when they're easier to debug.

    RESPONSIBILITY:
    - Validate workflow structure (required fields present)
    - Verify action handlers are callable
    - Check action configuration (retry settings, etc.)
    - Validate state transitions are valid
    - Report detailed validation errors

    PATTERNS:
    - Validator Pattern: Separate validation from business logic
    - Guard Clauses: Early return on validation failures
    - Accumulator: Collect all errors for complete report

    USAGE:
        validator = WorkflowValidator()
        result = validator.validate_workflow(workflow)
        if not result.is_valid:
            for error in result.errors:
                print(f"Validation error: {error}")
    """

    def validate_workflow(self, workflow: Workflow) -> ValidationResult:
        """
        Validate complete workflow

        WHAT:
        Performs comprehensive validation of workflow including structure,
        actions, and state transitions.

        WHY:
        Single entry point for workflow validation enables consistent
        validation across all workflows.

        ARGS:
            workflow: Workflow to validate

        RETURNS:
            ValidationResult with status and any errors

        VALIDATION CHECKS:
        - Workflow has name and issue type
        - Workflow has at least one action
        - All actions are valid
        - State transitions are valid
        """
        result = ValidationResult.success()

        # Guard: workflow must exist
        if workflow is None:
            result.add_error("Workflow is None")
            return result

        # Validate basic structure
        self._validate_workflow_structure(workflow, result)

        # Validate actions
        self._validate_actions(workflow, result)

        # Validate state transitions
        self._validate_state_transitions(workflow, result)

        return result

    def _validate_workflow_structure(
        self,
        workflow: Workflow,
        result: ValidationResult
    ) -> None:
        """
        Validate workflow has required fields

        CHECKS:
        - Name is present and non-empty
        - Issue type is valid IssueType enum
        - Actions list exists (can be empty for validation)
        - Success and failure states are defined
        """
        # Validate name
        if not hasattr(workflow, 'name') or not workflow.name:
            result.add_error("Workflow missing name")

        if hasattr(workflow, 'name') and not isinstance(workflow.name, str):
            result.add_error("Workflow name must be string")

        # Validate issue type
        if not hasattr(workflow, 'issue_type'):
            result.add_error("Workflow missing issue_type")
        elif not isinstance(workflow.issue_type, IssueType):
            result.add_error("Workflow issue_type must be IssueType enum")

        # Validate actions exist (list can be empty)
        if not hasattr(workflow, 'actions'):
            result.add_error("Workflow missing actions list")
        elif not isinstance(workflow.actions, list):
            result.add_error("Workflow actions must be list")

        # Validate state transitions exist
        if not hasattr(workflow, 'success_state'):
            result.add_error("Workflow missing success_state")
        elif not isinstance(workflow.success_state, PipelineState):
            result.add_error("Workflow success_state must be PipelineState enum")

        if not hasattr(workflow, 'failure_state'):
            result.add_error("Workflow missing failure_state")
        elif not isinstance(workflow.failure_state, PipelineState):
            result.add_error("Workflow failure_state must be PipelineState enum")

    def _validate_actions(
        self,
        workflow: Workflow,
        result: ValidationResult
    ) -> None:
        """
        Validate workflow actions

        CHECKS:
        - At least one action defined
        - All actions are WorkflowAction instances
        - Each action has required fields
        - Action handlers are callable
        - Retry configuration is valid
        """
        # Guard: actions must exist (checked in structure validation)
        if not hasattr(workflow, 'actions'):
            return

        actions = workflow.actions

        # Warn if no actions (unusual but not invalid)
        if not actions:
            result.add_warning(
                f"Workflow '{workflow.name}' has no actions"
            )
            return

        # Validate each action
        for i, action in enumerate(actions):
            self._validate_action(action, i, result)

    def _validate_action(
        self,
        action: WorkflowAction,
        index: int,
        result: ValidationResult
    ) -> None:
        """
        Validate single workflow action

        CHECKS:
        - Action is WorkflowAction instance
        - Action has name
        - Action has handler
        - Handler is callable
        - Retry configuration is valid
        """
        action_ref = f"Action {index}"

        # Validate action type
        if not isinstance(action, WorkflowAction):
            result.add_error(f"{action_ref} is not WorkflowAction instance")
            return

        # Validate action name
        if not hasattr(action, 'action_name') or not action.action_name:
            result.add_error(f"{action_ref} missing action_name")

        # Validate handler exists
        if not hasattr(action, 'handler'):
            result.add_error(f"{action_ref} missing handler")
            return

        # Validate handler is callable
        if not callable(action.handler):
            result.add_error(
                f"{action_ref} '{action.action_name}' handler is not callable"
            )

        # Validate retry configuration
        if hasattr(action, 'retry_on_failure') and action.retry_on_failure:
            if not hasattr(action, 'max_retries'):
                result.add_warning(
                    f"{action_ref} '{action.action_name}' has retry_on_failure "
                    "but no max_retries"
                )
            elif action.max_retries <= 0:
                result.add_error(
                    f"{action_ref} '{action.action_name}' max_retries must be positive"
                )

    def _validate_state_transitions(
        self,
        workflow: Workflow,
        result: ValidationResult
    ) -> None:
        """
        Validate state transitions are valid

        CHECKS:
        - Success and failure states are different
        - States are valid PipelineState values
        - Transitions make logical sense
        """
        # Guard: states must exist (checked in structure validation)
        if not hasattr(workflow, 'success_state') or not hasattr(workflow, 'failure_state'):
            return

        success_state = workflow.success_state
        failure_state = workflow.failure_state

        # Validate states are different
        if success_state == failure_state:
            result.add_warning(
                f"Workflow '{workflow.name}' has same success and failure state: "
                f"{success_state.name}"
            )

        # Validate success state is "forward progress"
        valid_success_states = {
            PipelineState.RUNNING,
            PipelineState.DEGRADED,
            PipelineState.COMPLETED
        }
        if success_state not in valid_success_states:
            result.add_warning(
                f"Workflow '{workflow.name}' has unusual success state: "
                f"{success_state.name}"
            )

        # Validate failure state indicates problem
        valid_failure_states = {
            PipelineState.FAILED,
            PipelineState.DEGRADED,
            PipelineState.HALTED
        }
        if failure_state not in valid_failure_states:
            result.add_warning(
                f"Workflow '{workflow.name}' has unusual failure state: "
                f"{failure_state.name}"
            )

    def validate_workflow_catalog(
        self,
        workflows: Dict[IssueType, Workflow]
    ) -> ValidationResult:
        """
        Validate complete workflow catalog

        WHAT:
        Validates all workflows in catalog and checks for completeness.

        WHY:
        Ensures all issue types have valid workflows and catches
        configuration errors across entire catalog.

        ARGS:
            workflows: Dict mapping issue types to workflows

        RETURNS:
            ValidationResult with status and any errors

        VALIDATION CHECKS:
        - All IssueType values have workflows
        - Each workflow is individually valid
        - No duplicate workflows for same issue type
        """
        result = ValidationResult.success()

        # Guard: workflows must exist
        if workflows is None:
            result.add_error("Workflow catalog is None")
            return result

        if not isinstance(workflows, dict):
            result.add_error("Workflow catalog must be dict")
            return result

        # Check completeness (all issue types have workflows)
        all_issue_types = set(IssueType)
        registered_types = set(workflows.keys())
        missing_types = all_issue_types - registered_types

        if missing_types:
            missing_names = [t.name for t in missing_types]
            result.add_error(
                f"Missing workflows for issue types: {', '.join(missing_names)}"
            )

        # Validate each workflow
        for issue_type, workflow in workflows.items():
            workflow_result = self.validate_workflow(workflow)

            # Add errors with context
            for error in workflow_result.errors:
                result.add_error(f"[{issue_type.name}] {error}")

            # Add warnings with context
            for warning in workflow_result.warnings:
                result.add_warning(f"[{issue_type.name}] {warning}")

        return result
