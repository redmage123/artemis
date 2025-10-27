#!/usr/bin/env python3
"""
Confidence Scorer (Layer 4: Retry with Refinement)

WHY: Aggregates validation signals from ALL layers into single confidence score.
     Determines if code quality meets threshold for acceptance.

RESPONSIBILITY: ONLY score confidence - no validation or retry logic.
PATTERNS: Strategy pattern for layer-specific scoring (no if/elif chains).

Example:
    scorer = ConfidenceScorer()
    score = scorer.score_confidence(validation_results)
    if score.confidence >= 0.85:
        accept_code()
"""

from typing import Dict, Optional
from dataclasses import dataclass

from artemis_stage_interface import LoggerInterface


@dataclass
class ConfidenceScore:
    """
    Confidence score from all validation layers.

    Attributes:
        confidence: Overall confidence (0.0-1.0)
        layer_scores: Individual scores from each layer
        passed_threshold: Whether confidence meets acceptance threshold
        recommendation: Accept/Retry/Reject
    """
    confidence: float
    layer_scores: Dict[str, float]
    passed_threshold: bool
    recommendation: str


class ConfidenceScorer:
    """
    Aggregates validation signals into confidence score.

    WHY: Single metric to judge code quality across all validation layers.
    PATTERNS: Strategy pattern for layer weighting (dictionary mapping).
    PERFORMANCE: O(1) score calculation.
    """

    # Layer weights (Strategy pattern - no if/elif)
    LAYER_WEIGHTS = {
        'streaming': 0.15,      # Layer 3.6
        'pipeline': 0.35,       # Layer 3
        'rag_similarity': 0.25, # Layer 3.5
        'completeness': 0.25    # Code completeness check
    }

    # Confidence thresholds (Strategy pattern)
    THRESHOLDS = {
        'accept': 0.85,  # Accept code if >= 0.85
        'retry': 0.50,   # Retry if >= 0.50 and < 0.85
        'reject': 0.50   # Reject if < 0.50
    }

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        acceptance_threshold: float = 0.85
    ):
        """Initialize confidence scorer."""
        self.logger = logger
        self.acceptance_threshold = acceptance_threshold

    def score_confidence(self, validation_results: Dict) -> ConfidenceScore:
        """
        Calculate confidence score from validation results.

        WHY: Combines multiple validation signals into single metric.
        PERFORMANCE: O(1) calculation with dictionary lookups.

        Args:
            validation_results: Results from all validation layers

        Returns:
            ConfidenceScore with overall confidence and recommendation
        """
        # Extract layer scores (Strategy pattern)
        layer_scores = self._extract_layer_scores(validation_results)

        # Calculate weighted confidence
        confidence = self._calculate_weighted_confidence(layer_scores)

        # Determine recommendation (Strategy pattern)
        recommendation = self._get_recommendation(confidence)

        passed_threshold = confidence >= self.acceptance_threshold

        if self.logger:
            self.logger.log(
                f"📊 Confidence: {confidence:.2f} ({recommendation})",
                "DEBUG"
            )

        return ConfidenceScore(
            confidence=confidence,
            layer_scores=layer_scores,
            passed_threshold=passed_threshold,
            recommendation=recommendation
        )

    def _extract_layer_scores(self, results: Dict) -> Dict[str, float]:
        """
        Extract scores from each validation layer.

        WHY: Normalizes different result formats into consistent scores.
        PATTERNS: Strategy pattern with extractor functions.
        """
        # Strategy pattern: layer → extractor mapping
        extractors = {
            'streaming': lambda r: 1.0 if r.get('streaming_passed', True) else 0.0,
            'pipeline': lambda r: 1.0 if r.get('passed', False) else 0.0,
            'rag_similarity': lambda r: r.get('rag_similarity', 0.5),
            'completeness': lambda r: r.get('completeness_score', 0.7)
        }

        return {
            layer: extractor(results)
            for layer, extractor in extractors.items()
        }

    def _calculate_weighted_confidence(self, layer_scores: Dict[str, float]) -> float:
        """
        Calculate weighted confidence from layer scores.

        WHY: Different layers have different importance.
        PERFORMANCE: Single pass calculation.
        """
        confidence = sum(
            layer_scores.get(layer, 0.0) * weight
            for layer, weight in self.LAYER_WEIGHTS.items()
        )

        return max(0.0, min(1.0, confidence))

    def _get_recommendation(self, confidence: float) -> str:
        """
        Get recommendation based on confidence.

        WHY: Clear decision on what to do with the code.
        PATTERNS: Strategy pattern with threshold mapping.
        """
        # Strategy pattern: threshold checks (early return)
        if confidence >= self.THRESHOLDS['accept']:
            return "ACCEPT"
        if confidence >= self.THRESHOLDS['retry']:
            return "RETRY"
        return "REJECT"
