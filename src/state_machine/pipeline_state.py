#!/usr/bin/env python3
"""
WHY: Define all possible states for the Artemis pipeline execution lifecycle
RESPONSIBILITY: Provide comprehensive enum of pipeline states with clear lifecycle paths
PATTERNS: State pattern foundation, enum-based state definitions
"""

from enum import Enum


class PipelineState(Enum):
    """
    Pipeline execution states

    Lifecycle:
    IDLE → INITIALIZING → RUNNING → COMPLETED/FAILED

    Recovery states:
    FAILED → RECOVERING → RUNNING (retry)
    FAILED → DEGRADED (partial success)
    FAILED → ABORTED (unrecoverable)
    """
    # Lifecycle states
    IDLE = "idle"                           # Not started
    INITIALIZING = "initializing"           # Setting up
    RUNNING = "running"                     # Active execution
    PAUSED = "paused"                       # Temporarily suspended
    COMPLETED = "completed"                 # Successfully finished
    FAILED = "failed"                       # Failed execution
    ABORTED = "aborted"                     # Manually aborted

    # Recovery states
    RECOVERING = "recovering"               # Attempting recovery
    DEGRADED = "degraded"                   # Partial success
    ROLLING_BACK = "rolling_back"          # Reverting changes

    # Stage-specific states
    STAGE_RUNNING = "stage_running"        # Individual stage executing
    STAGE_COMPLETED = "stage_completed"    # Stage completed
    STAGE_FAILED = "stage_failed"          # Stage failed
    STAGE_SKIPPED = "stage_skipped"        # Stage skipped (circuit open)
    STAGE_RETRYING = "stage_retrying"      # Stage retrying

    # Health states
    HEALTHY = "healthy"                     # All systems operational
    DEGRADED_HEALTH = "degraded_health"    # Some issues detected
    CRITICAL = "critical"                   # Critical failures
