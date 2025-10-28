#!/usr/bin/env python3
"""
Module: pipeline_state.py

WHY: Encapsulates pipeline lifecycle state management in a dedicated enum, enabling
     clear state transitions and validation across all pipeline operations.

RESPONSIBILITY: Define and document all valid pipeline states and their transitions.

PATTERNS:
    - State Pattern: Enables state-based behavior selection
    - Type Safety: Enum ensures only valid states used

State transitions:
    CREATED -> BUILDING -> READY -> RUNNING -> (PAUSED <-> RUNNING)* -> COMPLETED/FAILED
"""

from enum import Enum


class PipelineState(Enum):
    """
    Pipeline lifecycle states.

    Why needed: Enforces valid state transitions and enables State pattern
    implementation for lifecycle management.

    State transitions:
        CREATED -> BUILDING -> READY -> RUNNING -> (PAUSED <-> RUNNING)* -> COMPLETED/FAILED

    Design decision: Single enum ensures consistent state tracking across
    all pipeline instances and enables state-based behavior selection.
    """
    CREATED = "created"          # Pipeline object created, not configured
    BUILDING = "building"        # Builder is configuring pipeline
    READY = "ready"              # Built and validated, ready to execute
    RUNNING = "running"          # Currently executing stages
    PAUSED = "paused"           # Execution paused (can resume)
    COMPLETED = "completed"     # Successfully completed all stages
    FAILED = "failed"           # Failed with unrecoverable error
    CANCELLED = "cancelled"     # Cancelled by supervisor/user
