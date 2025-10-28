#!/usr/bin/env python3
"""
WHY: Build recovery workflows for LLM-related failures
RESPONSIBILITY: Construct recovery workflows for API errors, timeouts, rate limits, invalid responses
PATTERNS: Builder pattern, factory methods, workflow composition

LLM workflows handle:
- LLM API errors
- LLM timeouts
- Rate limit errors
- Invalid LLM responses

Each workflow defines actions to handle LLM service issues.
"""

from typing import Dict
from workflows_core.models import Workflow, WorkflowAction, IssueType, PipelineState
from workflow_handlers import WorkflowHandlers


class LLMWorkflowBuilder:
    """
    Build recovery workflows for LLM issues

    WHAT:
    Factory class that constructs recovery workflows for LLM-related failures:
    API errors, timeouts, rate limits, invalid responses.

    WHY:
    LLM services can be unreliable. This builder provides standardized
    recovery procedures for each type of LLM issue.

    PATTERNS:
    - Static Factory Methods: Each build_*_workflow() creates specific workflow
    - Builder Pattern: Constructs complex workflow objects step-by-step
    """

    @staticmethod
    def build_llm_api_error_workflow() -> Workflow:
        """
        Build workflow for LLM API error recovery

        ACTIONS:
        1. Retry LLM request
        2. Switch LLM provider if retry fails

        Returns workflow that attempts to recover from API errors.
        """
        return Workflow(
            name="LLM API Error Recovery",
            issue_type=IssueType.LLM_API_ERROR,
            actions=[
                WorkflowAction(
                    action_name="Retry LLM request",
                    handler=WorkflowHandlers.retry_llm_request,
                    retry_on_failure=True,
                    max_retries=3
                ),
                WorkflowAction(
                    action_name="Switch LLM provider",
                    handler=WorkflowHandlers.switch_llm_provider
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_llm_timeout_workflow() -> Workflow:
        """
        Build workflow for LLM timeout recovery

        ACTIONS:
        1. Retry LLM request with increased timeout

        Returns workflow that retries timed-out requests.
        """
        return Workflow(
            name="LLM Timeout Recovery",
            issue_type=IssueType.LLM_TIMEOUT,
            actions=[
                WorkflowAction(
                    action_name="Retry LLM request",
                    handler=WorkflowHandlers.retry_llm_request,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_llm_rate_limit_workflow() -> Workflow:
        """
        Build workflow for LLM rate limit handling

        ACTIONS:
        1. Handle rate limit (wait with exponential backoff)
        2. Switch LLM provider if persistent

        Returns workflow that handles rate limiting gracefully.
        """
        return Workflow(
            name="LLM Rate Limit Handling",
            issue_type=IssueType.LLM_RATE_LIMIT,
            actions=[
                WorkflowAction(
                    action_name="Handle rate limit",
                    handler=WorkflowHandlers.handle_rate_limit,
                    retry_on_failure=False
                ),
                WorkflowAction(
                    action_name="Switch LLM provider",
                    handler=WorkflowHandlers.switch_llm_provider
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.DEGRADED
        )

    @staticmethod
    def build_invalid_llm_response_workflow() -> Workflow:
        """
        Build workflow for invalid LLM response handling

        ACTIONS:
        1. Validate LLM response
        2. Retry LLM request if invalid

        Returns workflow that validates and retries invalid responses.
        """
        return Workflow(
            name="LLM Response Validation",
            issue_type=IssueType.INVALID_LLM_RESPONSE,
            actions=[
                WorkflowAction(
                    action_name="Validate LLM response",
                    handler=WorkflowHandlers.validate_llm_response
                ),
                WorkflowAction(
                    action_name="Retry LLM request",
                    handler=WorkflowHandlers.retry_llm_request,
                    retry_on_failure=True,
                    max_retries=2
                )
            ],
            success_state=PipelineState.RUNNING,
            failure_state=PipelineState.FAILED
        )

    @staticmethod
    def build_all() -> Dict[IssueType, Workflow]:
        """
        Build all LLM workflows

        Returns:
            Dict mapping IssueType to Workflow for all LLM issues
        """
        return {
            IssueType.LLM_API_ERROR: LLMWorkflowBuilder.build_llm_api_error_workflow(),
            IssueType.LLM_TIMEOUT: LLMWorkflowBuilder.build_llm_timeout_workflow(),
            IssueType.LLM_RATE_LIMIT: LLMWorkflowBuilder.build_llm_rate_limit_workflow(),
            IssueType.INVALID_LLM_RESPONSE: LLMWorkflowBuilder.build_invalid_llm_response_workflow(),
        }
