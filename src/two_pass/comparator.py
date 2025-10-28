"""
Module: two_pass/comparator.py

WHY: Compare first and second pass results to detect quality improvements.
RESPONSIBILITY: PassComparator for delta detection and quality validation.
PATTERNS: Strategy Pattern, Guard Clauses, Observer Pattern.

This module handles:
- Compare pass results
- Calculate quality deltas
- Emit comparison events

EXTRACTED FROM: two_pass_pipeline.py (lines 1121-1241, 121 lines)
"""

from typing import Optional, Dict, Any

from two_pass.models import PassResult, PassDelta
from two_pass.events import TwoPassEventType
from two_pass.exceptions import PassComparisonException
from artemis_exceptions import wrap_exception
from artemis_services import PipelineLogger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType

class PassComparator:
    """
    Compares pass results to detect deltas and quality changes.

    Why it exists: Validates that second pass improved upon first pass and
    calculates metrics for rollback decisions.

    Responsibilities:
    - Compare pass results
    - Detect quality improvements/degradations
    - Identify new artifacts and learnings
    - Calculate delta metrics
    - Emit comparison events

    Design pattern: Comparator + Observer
    """

    def __init__(self, observable: Optional[PipelineObservable] = None, verbose: bool = True):
        """Initialize comparator with observer integration"""
        self.observable = observable
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

    @wrap_exception(PassComparisonException, "Pass comparison failed")
    def compare(self, first_pass: PassResult, second_pass: PassResult) -> PassDelta:
        """
        Compare two pass results and calculate delta.

        What it does:
        1. Emit comparison start event
        2. Create PassDelta (auto-calculates metrics in __post_init__)
        3. Determine quality change type
        4. Emit appropriate event based on quality change
        5. Return delta for analysis

        Args:
            first_pass: First pass result
            second_pass: Second pass result

        Returns:
            PassDelta with comparison metrics

        Raises:
            PassComparisonException: On comparison failure
        """
        self._emit_event(
            TwoPassEventType.PASS_COMPARISON_STARTED,
            {
                "first_pass_quality": first_pass.quality_score,
                "second_pass_quality": second_pass.quality_score
            }
        )

        # Create delta - automatically calculates all metrics
        delta = PassDelta(first_pass=first_pass, second_pass=second_pass)

        # Emit quality change event - dispatch table instead of if/elif
        quality_event_map = {
            "improved": TwoPassEventType.PASS_QUALITY_IMPROVED,
            "degraded": TwoPassEventType.PASS_QUALITY_DEGRADED,
            "unchanged": TwoPassEventType.PASS_QUALITY_UNCHANGED
        }

        quality_change = self._classify_quality_change(delta.quality_delta)
        event_type = quality_event_map[quality_change]

        self._emit_event(
            event_type,
            {
                "quality_delta": delta.quality_delta,
                "new_artifacts_count": len(delta.new_artifacts),
                "new_learnings_count": len(delta.new_learnings),
                "execution_time_delta": delta.execution_time_delta
            }
        )

        return delta

    def _classify_quality_change(self, quality_delta: float, threshold: float = 0.01) -> str:
        """
        Classify quality change type (helper method).

        Why extracted: Encapsulates quality classification logic. Uses threshold
        to avoid noise from tiny fluctuations.

        Args:
            quality_delta: Difference in quality scores
            threshold: Minimum delta to consider changed (default 1%)

        Returns:
            "improved", "degraded", or "unchanged"
        """
        if quality_delta > threshold:
            return "improved"
        elif quality_delta < -threshold:
            return "degraded"
        else:
            return "unchanged"

    def _emit_event(self, event_type: TwoPassEventType, data: Dict[str, Any]) -> None:
        """Emit event to observers (helper method)"""
        # Guard clause - early return if no observable
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            stage_name="PassComparator",
            data={
                "two_pass_event": event_type.value,
                **data
            }
        )

        self.observable.notify(event)


# ============================================================================
# ROLLBACK MANAGER - Handles rollback to first pass
# ============================================================================


__all__ = ['PassComparator']
