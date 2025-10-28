"""
Module: two_pass/events.py

WHY: Event types for two-pass pipeline monitoring.
RESPONSIBILITY: Define event taxonomy for first pass, second pass, delta detection, rollback.
PATTERNS: Enum Pattern.

EXTRACTED FROM: two_pass_pipeline.py (lines 94-144, 50 lines)
"""

from enum import Enum


class TwoPassEventType(Enum):
    """
    Event types specific to two-pass pipeline operations.

    Why needed: Extends EventType with two-pass specific events for granular monitoring
    of first pass, second pass, delta detection, and rollback operations.

    Categories:
    - First pass lifecycle: FIRST_PASS_STARTED, FIRST_PASS_COMPLETED, FIRST_PASS_FAILED
    - Second pass lifecycle: SECOND_PASS_STARTED, SECOND_PASS_COMPLETED, SECOND_PASS_FAILED
    - Pass comparison: PASS_DELTA_DETECTED, PASS_QUALITY_IMPROVED, PASS_QUALITY_DEGRADED
    - State management: MEMENTO_CREATED, MEMENTO_APPLIED, ROLLBACK_INITIATED
    - Learning: LEARNING_CAPTURED, INSIGHT_APPLIED
    """

    # First pass events
    FIRST_PASS_STARTED = "first_pass_started"
    FIRST_PASS_COMPLETED = "first_pass_completed"
    FIRST_PASS_FAILED = "first_pass_failed"
    FIRST_PASS_ANALYSIS_COMPLETED = "first_pass_analysis_completed"

    # Second pass events
    SECOND_PASS_STARTED = "second_pass_started"
    SECOND_PASS_COMPLETED = "second_pass_completed"
    SECOND_PASS_FAILED = "second_pass_failed"
    SECOND_PASS_REFINED = "second_pass_refined"

    # Delta and comparison events
    PASS_DELTA_DETECTED = "pass_delta_detected"
    PASS_COMPARISON_STARTED = "pass_comparison_started"
    PASS_COMPARISON_COMPLETED = "pass_comparison_completed"
    PASS_QUALITY_IMPROVED = "pass_quality_improved"
    PASS_QUALITY_DEGRADED = "pass_quality_degraded"
    PASS_QUALITY_UNCHANGED = "pass_quality_unchanged"

    # State management events
    MEMENTO_CREATED = "memento_created"
    MEMENTO_APPLIED = "memento_applied"
    MEMENTO_RESTORED = "memento_restored"

    # Rollback events
    ROLLBACK_INITIATED = "rollback_initiated"
    ROLLBACK_COMPLETED = "rollback_completed"
    ROLLBACK_FAILED = "rollback_failed"

    # Learning events
    LEARNING_CAPTURED = "learning_captured"
    INSIGHT_APPLIED = "insight_applied"
    INCREMENTAL_IMPROVEMENT = "incremental_improvement"


__all__ = ["TwoPassEventType"]
