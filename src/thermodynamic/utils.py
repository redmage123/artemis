"""
Module: thermodynamic/utils.py

WHY: Utility functions for thermodynamic computing.
RESPONSIBILITY: Helper functions for confidence checking, risk assessment.
PATTERNS: Functional Programming, Guard Clauses.

This module handles:
- check_confidence_threshold(): Threshold checking with event emission
- assess_risk(): Risk level assessment from confidence scores

EXTRACTED FROM: thermodynamic_computing.py (lines 2454-2600+)
"""

from typing import Dict, Any, Optional
from thermodynamic.models import ConfidenceScore
from thermodynamic.events import ThermodynamicEventType
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from artemis_exceptions import PipelineException, wrap_exception


def check_confidence_threshold(
    score: ConfidenceScore,
    threshold: float,
    observable: Optional[PipelineObservable] = None,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Check if confidence score meets threshold.

    Args:
        score: ConfidenceScore to check
        threshold: Minimum confidence required
        observable: Optional observable for event emission
        context: Optional context for events

    Returns:
        True if confidence >= threshold

    Emits:
        CONFIDENCE_THRESHOLD_EXCEEDED or CONFIDENCE_THRESHOLD_FAILED event
    """
    # Check threshold
    meets_threshold = score.confidence >= threshold

    # Emit event
    if observable:
        event_type = (
            ThermodynamicEventType.CONFIDENCE_THRESHOLD_EXCEEDED
            if meets_threshold
            else ThermodynamicEventType.CONFIDENCE_THRESHOLD_FAILED
        )

        event_data = {
            "thermodynamic_event": event_type.value,
            "confidence": score.confidence,
            "threshold": threshold,
            "meets_threshold": meets_threshold
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id") if context else None,
            stage_name=context.get("stage") if context else None,
            data=event_data
        )

        observable.notify(event)

    return meets_threshold


@wrap_exception(PipelineException, "Risk assessment failed")
def assess_risk(
    score: ConfidenceScore,
    risk_threshold: float = 0.3,
    observable: Optional[PipelineObservable] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Assess risk level based on confidence score.

    Args:
        score: ConfidenceScore to assess
        risk_threshold: Variance threshold for high risk
        observable: Optional observable for events
        context: Optional context

    Returns:
        Dict with risk_level, confidence, variance, recommendations
    """
    # Determine risk level
    c = score.confidence
    v = score.variance

    if c < 0.5 or v > risk_threshold:
        risk_level = "high"
        recommendations = [
            "Gather more evidence",
            "Run additional simulations",
            "Request human review"
        ]
    elif c < 0.7 or v > risk_threshold * 0.5:
        risk_level = "medium"
        recommendations = [
            "Monitor closely",
            "Consider additional validation"
        ]
    else:
        risk_level = "low"
        recommendations = []

    # Emit risk assessment event
    if observable:
        event_data = {
            "thermodynamic_event": ThermodynamicEventType.RISK_ASSESSED.value,
            "risk_level": risk_level,
            "confidence": c,
            "variance": v
        }

        event = PipelineEvent(
            event_type=EventType.STAGE_PROGRESS,
            card_id=context.get("card_id") if context else None,
            stage_name=context.get("stage") if context else None,
            data=event_data
        )

        observable.notify(event)

    return {
        "risk_level": risk_level,
        "confidence": c,
        "variance": v,
        "recommendations": recommendations
    }


__all__ = [
    "check_confidence_threshold",
    "assess_risk"
]
