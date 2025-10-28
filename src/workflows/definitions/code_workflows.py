#!/usr/bin/env python3
"""
Code Quality Workflow Definitions

WHAT:
Recovery workflows for code-related failures including compilation errors,
test failures, security vulnerabilities, and linting issues.

WHY:
Code quality issues are detected during build and validation stages.
These workflows provide automated fixes for common code problems.

RESPONSIBILITY:
- Define recovery workflows for code quality failures
- Configure retry strategies for flaky tests
- Set state transitions for recoverable vs. fatal errors

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Retry Strategy: Different retry counts for different failure types
- Degraded State: Some failures allow pipeline to continue with warnings

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for action execution
- Returns: Workflow objects with configured actions
"""

from typing import Dict, Any, Optional, List, Callable
from state_machine import (
    IssueType,
    Workflow,
    WorkflowAction,
    PipelineState
)
from workflow_handlers import WorkflowHandlers


# ============================================================================
# CODE QUALITY WORKFLOW BUILDERS
# ============================================================================

def build_compilation_error_workflow() -> Workflow:
    """
    Build workflow for compilation error recovery

    WHAT:
    Creates workflow to retry compilation with potential fixes.

    WHY:
    Some compilation errors are transient (race conditions, temp file issues).
    Retry can resolve these without code changes.

    STRATEGY:
    1. Retry compilation (up to 2 times)

    RETURNS:
        Workflow: Configured compilation error recovery workflow
    """
    return Workflow(
        name="Compilation Error Recovery",
        issue_type=IssueType.COMPILATION_ERROR,
        actions=[
            WorkflowAction(
                action_name="Retry compilation",
                handler=WorkflowHandlers.retry_compilation,
                retry_on_failure=True,
                max_retries=2
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_test_failure_workflow() -> Workflow:
    """
    Build workflow for test failure recovery

    WHAT:
    Creates workflow to rerun failed tests to detect flaky tests.

    WHY:
    Tests can fail due to timing issues, race conditions, or environmental
    factors. Rerunning helps distinguish real failures from flaky tests.

    STRATEGY:
    1. Rerun tests (up to 2 times)

    RETURNS:
        Workflow: Configured test failure recovery workflow
    """
    return Workflow(
        name="Test Failure Recovery",
        issue_type=IssueType.TEST_FAILURE,
        actions=[
            WorkflowAction(
                action_name="Rerun tests",
                handler=WorkflowHandlers.rerun_tests,
                retry_on_failure=True,
                max_retries=2
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_security_vulnerability_workflow() -> Workflow:
    """
    Build workflow for security vulnerability fixes

    WHAT:
    Creates workflow to apply automated security patches.

    WHY:
    Security vulnerabilities must be addressed before deployment.
    Automated patching can fix known CVEs without manual intervention.

    STRATEGY:
    1. Apply security patch (no retry - patch either works or doesn't)

    RETURNS:
        Workflow: Configured security vulnerability fix workflow
    """
    return Workflow(
        name="Security Vulnerability Fix",
        issue_type=IssueType.SECURITY_VULNERABILITY,
        actions=[
            WorkflowAction(
                action_name="Apply security patch",
                handler=WorkflowHandlers.fix_security_vulnerability
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.FAILED
    )


def build_linting_error_workflow() -> Workflow:
    """
    Build workflow for linting error fixes

    WHAT:
    Creates workflow to auto-fix linting issues using linter tools.

    WHY:
    Most linting errors are formatting issues that can be auto-fixed.
    Running linter in fix mode resolves these automatically.

    STRATEGY:
    1. Run linter auto-fix (most linters support --fix flag)

    NOTE:
    Linting failures don't stop pipeline (DEGRADED state) but are tracked.

    RETURNS:
        Workflow: Configured linting error fix workflow
    """
    return Workflow(
        name="Linting Error Fix",
        issue_type=IssueType.LINTING_ERROR,
        actions=[
            WorkflowAction(
                action_name="Run linter auto-fix",
                handler=WorkflowHandlers.run_linter_fix
            )
        ],
        success_state=PipelineState.RUNNING,
        failure_state=PipelineState.DEGRADED
    )


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_code_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all code quality recovery workflows

    WHAT:
    Returns complete mapping of code issue types to workflows.

    WHY:
    Provides single point of access for all code quality workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: Code quality workflows by issue type
    """
    return {
        IssueType.COMPILATION_ERROR: build_compilation_error_workflow(),
        IssueType.TEST_FAILURE: build_test_failure_workflow(),
        IssueType.SECURITY_VULNERABILITY: build_security_vulnerability_workflow(),
        IssueType.LINTING_ERROR: build_linting_error_workflow(),
    }
