#!/usr/bin/env python3
"""
State Machine Package - Pipeline State Tracking and Management

This package provides comprehensive state management for the Artemis pipeline,
including state transitions, workflow orchestration, and recovery mechanisms.

Architecture:
- Enums: PipelineState, StageState, EventType, IssueType
- Models: StateTransition, StageStateInfo, WorkflowExecution, PipelineSnapshot
- Workflows: WorkflowAction, Workflow
- Core: ArtemisStateMachine (backward compatible wrapper)
- Modular Components:
  * StateValidator - Transition validation
  * StateTransitionEngine - State transitions with history
  * WorkflowExecutor - Workflow execution and recovery
  * LLMWorkflowGenerator - Dynamic workflow generation
  * PushdownAutomaton - State stack for rollback
  * CheckpointIntegration - Checkpoint/resume functionality
  * StatePersistence - State save/load
  * StageStateManager - Individual stage tracking
  * ArtemisStateMachineCore - Main orchestrator facade
- Factory: create_state_machine()

Key Features:
- Event-driven state transitions with validation
- Workflow orchestration for issue recovery
- State history and audit trail
- Snapshot/restore capabilities
- Pushdown automaton for rollback support
- Checkpoint/resume integration
"""

# Enums
from state_machine.pipeline_state import PipelineState
from state_machine.stage_state import StageState
from state_machine.event_type import EventType
from state_machine.issue_type import IssueType

# Data models
from state_machine.state_transition import StateTransition
from state_machine.stage_state_info import StageStateInfo
from state_machine.workflow_execution import WorkflowExecution
from state_machine.pipeline_snapshot import PipelineSnapshot

# Workflow components
from state_machine.workflow_action import WorkflowAction
from state_machine.workflow import Workflow

# Modular components (new architecture)
from state_machine.state_validator import StateValidator
from state_machine.state_transition_engine import StateTransitionEngine
from state_machine.workflow_executor import WorkflowExecutor
from state_machine.llm_workflow_generator import LLMWorkflowGenerator
from state_machine.pushdown_automaton import PushdownAutomaton
from state_machine.checkpoint_integration import CheckpointIntegration
from state_machine.state_persistence import StatePersistence
from state_machine.stage_state_manager import StageStateManager
from state_machine.state_machine_core import ArtemisStateMachineCore

# Core state machine (backward compatible wrapper)
from state_machine.artemis_state_machine import ArtemisStateMachine

# Factory
from state_machine.factory import create_state_machine

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

    # Modular components (new)
    "StateValidator",
    "StateTransitionEngine",
    "WorkflowExecutor",
    "LLMWorkflowGenerator",
    "PushdownAutomaton",
    "CheckpointIntegration",
    "StatePersistence",
    "StageStateManager",
    "ArtemisStateMachineCore",

    # Core (backward compatible)
    "ArtemisStateMachine",

    # Factory
    "create_state_machine",
]
