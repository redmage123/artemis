#!/usr/bin/env python3
"""
WHY: Build recovery workflows for code-related failures (compilation, tests, security, linting)
RESPONSIBILITY: Construct recovery workflows for code quality and build issues
PATTERNS: Builder pattern, factory methods, workflow composition

Code workflows handle:
- Compilation errors
- Test failures
- Security vulnerabilities
- Linting errors

Each workflow defines actions to diagnose and fix code-related issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class CodeWorkflowBuilder:
    """
    Build recovery workflows for code issues

    WHAT:
    Factory class that constructs recovery workflows for code-related failures:
    compilation errors, test failures, security vulnerabilities, linting errors.

    WHY:
    Code issues are frequent in development. This builder provides standardized
    recovery procedures for each type of code issue.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_compilation_error_workflow() -> Workflow:
        """
        Build workflow for compilation error recovery

        ACTIONS:
        1. Retry compilation with clean build

        Returns workflow that attempts to resolve compilation issues.
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

    @staticmethod
    def build_test_failure_workflow() -> Workflow:
        """
        Build workflow for test failure recovery

        ACTIONS:
        1. Rerun tests (may be flaky tests)

        Returns workflow that retries failed tests.
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

    @staticmethod
    def build_security_vulnerability_workflow() -> Workflow:
        """
        Build workflow for security vulnerability fix

        ACTIONS:
        1. Apply security patch

        Returns workflow that applies security fixes.
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

    @staticmethod
    def build_linting_error_workflow() -> Workflow:
        """
        Build workflow for linting error fix

        ACTIONS:
        1. Run linter auto-fix

        Returns workflow that applies linter auto-fixes.
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

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all code workflows

        Returns:
            Dict mapping IssueType to Workflow for all code issues
        """
        return {
            IssueType.COMPILATION_ERROR: CodeWorkflowBuilder.build_compilation_error_workflow(),
            IssueType.TEST_FAILURE: CodeWorkflowBuilder.build_test_failure_workflow(),
            IssueType.SECURITY_VULNERABILITY: CodeWorkflowBuilder.build_security_vulnerability_workflow(),
            IssueType.LINTING_ERROR: CodeWorkflowBuilder.build_linting_error_workflow(),
        }
