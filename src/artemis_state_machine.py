#!/usr/bin/env python3
"""
Artemis State Machine - Pipeline State Tracking and Management

BACKWARD COMPATIBILITY WRAPPER
This module re-exports all components from the state_machine package.
All new code should import from state_machine package directly.

Example:
    # Old (still works):
    from artemis_state_machine import ArtemisStateMachine, PipelineState

    # New (preferred):
    from state_machine import ArtemisStateMachine, PipelineState
"""

# Re-export all public components for backward compatibility
from state_machine import (
    # Enums
    PipelineState,
    StageState,
    EventType,
    IssueType,

    # Data models
    StateTransition,
    StageStateInfo,
    WorkflowExecution,
    PipelineSnapshot,

    # Workflow components
    WorkflowAction,
    Workflow,

    # Core
    ArtemisStateMachine,

    # Factory
    create_state_machine,
)

__all__ = [
    # Enums
    "PipelineState",
    "StageState",
    "EventType",
    "IssueType",

    # Data models
    "StateTransition",
    "StageStateInfo",
    "WorkflowExecution",
    "PipelineSnapshot",

    # Workflow components
    "WorkflowAction",
    "Workflow",

    # Core
    "ArtemisStateMachine",

    # Factory
    "create_state_machine",
]
