#!/usr/bin/env python3
"""
WHY: Define events that trigger state transitions in the pipeline
RESPONSIBILITY: Enumerate all transition triggers for event-driven state machine
PATTERNS: Event-driven architecture, state machine transitions
"""

from enum import Enum


class EventType(Enum):
    """Events that trigger state transitions"""
    # Lifecycle events
    START = "start"
    COMPLETE = "complete"
    FAIL = "fail"
    ABORT = "abort"
    PAUSE = "pause"
    RESUME = "resume"

    # Stage events
    STAGE_START = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    STAGE_FAIL = "stage_fail"
    STAGE_RETRY = "stage_retry"
    STAGE_SKIP = "stage_skip"
    STAGE_TIMEOUT = "stage_timeout"

    # Recovery events
    RECOVERY_START = "recovery_start"
    RECOVERY_SUCCESS = "recovery_success"
    RECOVERY_FAIL = "recovery_fail"
    ROLLBACK_START = "rollback_start"
    ROLLBACK_COMPLETE = "rollback_complete"

    # Health events
    HEALTH_DEGRADED = "health_degraded"
    HEALTH_CRITICAL = "health_critical"
    HEALTH_RESTORED = "health_restored"

    # Circuit breaker events
    CIRCUIT_OPEN = "circuit_open"
    CIRCUIT_CLOSE = "circuit_close"
