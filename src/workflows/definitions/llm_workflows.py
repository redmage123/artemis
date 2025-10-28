#!/usr/bin/env python3
"""
LLM Integration Workflow Definitions

WHAT:
Recovery workflows for LLM-related failures including API errors, timeouts,
rate limits, and invalid responses.

WHY:
LLM operations are critical to Artemis but can fail due to API issues,
network problems, or response quality. These workflows provide resilience
through retries, fallbacks, and provider switching.

RESPONSIBILITY:
- Define recovery workflows for LLM failures
- Configure retry strategies with exponential backoff
- Handle rate limiting and provider failover

PATTERNS:
- Builder Pattern: Each build_* method constructs a complete workflow
- Circuit Breaker: Rate limit handling with backoff
- Fallback Chain: Primary LLM -> Backup LLM provider

INTEGRATION:
- Used by: WorkflowBuilder, WorkflowRegistry
- Uses: workflow_handlers for LLM operations
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
# LLM WORKFLOW BUILDERS
# ============================================================================

def build_llm_api_error_workflow() -> Workflow:
    """
    Build workflow for LLM API error recovery

    WHAT:
    Creates workflow to handle LLM API failures through retry and provider switching.

    WHY:
    LLM APIs can fail due to service issues, network problems, or quota limits.
    Retry with backoff usually succeeds, but provider switching provides fallback.

    STRATEGY:
    1. Retry LLM request (up to 3 times with exponential backoff)
    2. Switch LLM provider (fallback if retries fail)

    RETURNS:
        Workflow: Configured LLM API error recovery workflow
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


def build_llm_timeout_workflow() -> Workflow:
    """
    Build workflow for LLM timeout recovery

    WHAT:
    Creates workflow to retry timed-out LLM requests.

    WHY:
    LLM timeouts occur when responses take longer than expected. This can be
    due to complex prompts, high load, or network latency. Retry usually succeeds.

    STRATEGY:
    1. Retry LLM request (up to 2 times)

    NOTE:
    Timeout handling should include increasing timeout threshold in handler.

    RETURNS:
        Workflow: Configured LLM timeout recovery workflow
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


def build_llm_rate_limit_workflow() -> Workflow:
    """
    Build workflow for LLM rate limit handling

    WHAT:
    Creates workflow to handle rate limiting with backoff and provider switching.

    WHY:
    Rate limits protect LLM services from overload. Waiting and retrying respects
    limits, while provider switching provides immediate fallback.

    STRATEGY:
    1. Handle rate limit (exponential backoff based on retry-after header)
    2. Switch LLM provider (immediate fallback if rate limit persists)

    RETURNS:
        Workflow: Configured rate limit handling workflow
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


def build_invalid_llm_response_workflow() -> Workflow:
    """
    Build workflow for invalid LLM response handling

    WHAT:
    Creates workflow to validate and retry invalid LLM responses.

    WHY:
    LLMs can produce malformed JSON, incomplete responses, or incorrect formats.
    Validation and retry with clearer prompts often resolves the issue.

    STRATEGY:
    1. Validate LLM response (check format, completeness, schema)
    2. Retry LLM request (up to 2 times with improved prompt)

    RETURNS:
        Workflow: Configured invalid response handling workflow
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


# ============================================================================
# WORKFLOW CATALOG
# ============================================================================

def get_llm_workflows() -> Dict[IssueType, Workflow]:
    """
    Get all LLM integration workflows

    WHAT:
    Returns complete mapping of LLM issue types to workflows.

    WHY:
    Provides single point of access for all LLM workflows.
    Used by WorkflowRegistry to build complete workflow catalog.

    RETURNS:
        Dict[IssueType, Workflow]: LLM workflows by issue type
    """
    return {
        IssueType.LLM_API_ERROR: build_llm_api_error_workflow(),
        IssueType.LLM_TIMEOUT: build_llm_timeout_workflow(),
        IssueType.LLM_RATE_LIMIT: build_llm_rate_limit_workflow(),
        IssueType.INVALID_LLM_RESPONSE: build_invalid_llm_response_workflow(),
    }
