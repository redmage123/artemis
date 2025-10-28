#!/usr/bin/env python3
"""
Module: observer/event_types.py

WHY: Centralized enum of all event types in the Artemis pipeline,
     ensuring type safety and preventing string typos. Enables IDE autocomplete
     and compile-time checking.

RESPONSIBILITY:
    - Define all pipeline event types as strongly-typed enum
    - Categorize events by lifecycle phase (pipeline, stage, developer, etc.)
    - Provide single source of truth for event naming

PATTERNS:
    - Enum pattern for type-safe constants
    - Category grouping via comments for maintainability
    - Value-based enum for string serialization

DESIGN DECISIONS:
    - Single enum for all event types provides centralized event catalog
    - Prevents event name collisions across system
    - String values enable JSON serialization and human-readable logs
"""

from enum import Enum


class EventType(Enum):
    """
    Types of pipeline events.

    Categories:
    - Pipeline lifecycle: PIPELINE_STARTED, PIPELINE_COMPLETED, PIPELINE_FAILED
    - Stage lifecycle: STAGE_STARTED, STAGE_COMPLETED, STAGE_FAILED, STAGE_SKIPPED
    - Developer: DEVELOPER_STARTED, DEVELOPER_COMPLETED, DEVELOPER_FAILED
    - Code review: CODE_REVIEW_*
    - Validation: VALIDATION_*
    - Integration: INTEGRATION_*
    - Workflow: WORKFLOW_*
    - Supervisor commands: SUPERVISOR_COMMAND_* (bidirectional control)
    - Agent responses: AGENT_COMMAND_*, AGENT_STATUS_*
    - Git operations: GIT_*
    """

    # Pipeline lifecycle
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    PIPELINE_PAUSED = "pipeline_paused"
    PIPELINE_RESUMED = "pipeline_resumed"

    # Stage lifecycle
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"
    STAGE_SKIPPED = "stage_skipped"
    STAGE_RETRYING = "stage_retrying"
    STAGE_PROGRESS = "stage_progress"

    # Developer events
    DEVELOPER_STARTED = "developer_started"
    DEVELOPER_COMPLETED = "developer_completed"
    DEVELOPER_FAILED = "developer_failed"

    # Code review events
    CODE_REVIEW_STARTED = "code_review_started"
    CODE_REVIEW_COMPLETED = "code_review_completed"
    CODE_REVIEW_FAILED = "code_review_failed"

    # Validation events
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_FAILED = "validation_failed"

    # Integration events
    INTEGRATION_STARTED = "integration_started"
    INTEGRATION_COMPLETED = "integration_completed"
    INTEGRATION_CONFLICT = "integration_conflict"

    # Workflow events
    WORKFLOW_TRIGGERED = "workflow_triggered"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"

    # Supervisor command events (bidirectional communication)
    SUPERVISOR_COMMAND_PAUSE = "supervisor_command_pause"
    SUPERVISOR_COMMAND_RESUME = "supervisor_command_resume"
    SUPERVISOR_COMMAND_CANCEL = "supervisor_command_cancel"
    SUPERVISOR_COMMAND_RETRY = "supervisor_command_retry"
    SUPERVISOR_COMMAND_SKIP = "supervisor_command_skip"
    SUPERVISOR_COMMAND_OVERRIDE = "supervisor_command_override"
    SUPERVISOR_COMMAND_FORCE_APPROVAL = "supervisor_command_force_approval"
    SUPERVISOR_COMMAND_FORCE_REJECTION = "supervisor_command_force_rejection"
    SUPERVISOR_COMMAND_SELECT_WINNER = "supervisor_command_select_winner"
    SUPERVISOR_COMMAND_CHANGE_PRIORITY = "supervisor_command_change_priority"
    SUPERVISOR_COMMAND_ADJUST_TIMEOUT = "supervisor_command_adjust_timeout"
    SUPERVISOR_COMMAND_REQUEST_STATUS = "supervisor_command_request_status"
    SUPERVISOR_COMMAND_EMERGENCY_STOP = "supervisor_command_emergency_stop"

    # Agent response events
    AGENT_COMMAND_ACKNOWLEDGED = "agent_command_acknowledged"
    AGENT_COMMAND_COMPLETED = "agent_command_completed"
    AGENT_COMMAND_FAILED = "agent_command_failed"
    AGENT_STATUS_RESPONSE = "agent_status_response"

    # Git Agent events
    GIT_REPOSITORY_CONFIGURED = "git_repository_configured"
    GIT_BRANCH_CREATED = "git_branch_created"
    GIT_BRANCH_SWITCHED = "git_branch_switched"
    GIT_BRANCH_DELETED = "git_branch_deleted"
    GIT_COMMIT_CREATED = "git_commit_created"
    GIT_PUSH_STARTED = "git_push_started"
    GIT_PUSH_COMPLETED = "git_push_completed"
    GIT_PUSH_FAILED = "git_push_failed"
    GIT_PULL_STARTED = "git_pull_started"
    GIT_PULL_COMPLETED = "git_pull_completed"
    GIT_PULL_FAILED = "git_pull_failed"
    GIT_TAG_CREATED = "git_tag_created"
    GIT_MERGE_STARTED = "git_merge_started"
    GIT_MERGE_COMPLETED = "git_merge_completed"
    GIT_MERGE_CONFLICT = "git_merge_conflict"
    GIT_OPERATION_FAILED = "git_operation_failed"
