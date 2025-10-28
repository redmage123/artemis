#!/usr/bin/env python3
"""
Module: feature_prioritizer.py

WHY: Prioritize features using weighted scoring algorithm
RESPONSIBILITY: Rank features by business value, complexity, and risk
PATTERNS: Strategy pattern for configurable prioritization weights
"""

from typing import List, Dict
from sprint_models import Feature, PrioritizedFeature, RiskLevel
from planning_poker import FeatureEstimate


class FeaturePrioritizer:
    """
    WHY: Not all features are equal; need optimal sprint allocation
    RESPONSIBILITY: Calculate priority scores and rank features
    PATTERNS: Strategy pattern with configurable weights
    """

    # Dispatch table for risk score mapping
    RISK_SCORES: Dict[str, float] = {
        'low': 1.0,
        'medium': 2.0,
        'high': 3.0
    }

    def __init__(
        self,
        priority_weight: float = 0.4,
        value_weight: float = 0.3,
        risk_weight: float = 0.3
    ):
        """
        WHY: Configurable weights enable different prioritization strategies

        Args:
            priority_weight: Weight for feature priority (0-1)
            value_weight: Weight for business value (0-1)
            risk_weight: Weight for risk penalty (0-1)
        """
        self.priority_weight = priority_weight
        self.value_weight = value_weight
        self.risk_weight = risk_weight

    def prioritize(
        self,
        features: List[Feature],
        estimates: List[FeatureEstimate]
    ) -> List[PrioritizedFeature]:
        """
        WHY: Optimal sprint allocation requires prioritized feature list
        RESPONSIBILITY: Calculate scores and sort features by priority
        PATTERNS: Guard clauses, list comprehension

        Args:
            features: List of Feature objects
            estimates: List of FeatureEstimate objects (same order as features)

        Returns:
            List of PrioritizedFeature objects sorted by priority (descending)
        """
        # Guard: Empty lists
        if not features or not estimates:
            return []

        # Guard: Mismatched lengths
        if len(features) != len(estimates):
            raise ValueError(
                f"Feature count ({len(features)}) must match "
                f"estimate count ({len(estimates)})"
            )

        prioritized = [
            self._create_prioritized_feature(feature, estimate)
            for feature, estimate in zip(features, estimates)
        ]

        # Sort by priority score (descending = highest priority first)
        prioritized.sort(key=lambda x: x.priority_score, reverse=True)

        return prioritized

    def _create_prioritized_feature(
        self,
        feature: Feature,
        estimate: FeatureEstimate
    ) -> PrioritizedFeature:
        """
        WHY: Encapsulate priority score calculation logic
        RESPONSIBILITY: Create PrioritizedFeature from Feature and Estimate
        """
        risk_score = self._get_risk_score(estimate.risk_level)
        priority_score = self._calculate_priority_score(
            feature.business_value,
            estimate.final_estimate,
            risk_score
        )

        return PrioritizedFeature(
            feature=feature,
            story_points=estimate.final_estimate,
            estimated_hours=estimate.estimated_hours,
            risk_level=RiskLevel(estimate.risk_level),
            confidence=estimate.confidence,
            priority_score=priority_score
        )

    def _get_risk_score(self, risk_level: str) -> float:
        """
        WHY: Convert risk level string to numeric score
        RESPONSIBILITY: Lookup risk score from dispatch table
        PATTERNS: Dispatch table instead of if/elif chain
        """
        return self.RISK_SCORES.get(risk_level.lower(), 2.0)

    def _calculate_priority_score(
        self,
        business_value: int,
        story_points: int,
        risk_score: float
    ) -> float:
        """
        WHY: Weighted scoring balances value, effort, and risk
        RESPONSIBILITY: Apply configured weights to calculate final score

        Formula:
            priority = (business_value * priority_weight) +
                      (story_points * value_weight) -
                      (risk_score * risk_weight)

        Higher score = higher priority
        """
        return (
            business_value * self.priority_weight +
            story_points * self.value_weight -
            risk_score * self.risk_weight
        )
