#!/usr/bin/env python3
"""
Review Scorer - Overall Review Score Calculation

WHY: Calculate weighted overall review score from multiple review dimensions
RESPONSIBILITY: Combine architecture, sprint, and quality scores with configurable weights
PATTERNS: Single Responsibility, Configuration-Driven Weights, Guard Clauses

This module:
- Combines multiple review dimensions
- Applies configurable weights
- Makes approval/rejection decisions
- Handles score thresholds
"""

from typing import Dict, List, Any, Tuple


class ReviewScorer:
    """
    Calculates overall review score and makes approval decisions

    WHY: Centralize scoring logic with configurable weights
    RESPONSIBILITY: Weighted score calculation and threshold-based decisions
    """

    def __init__(
        self,
        review_weights: Dict[str, float],
        logger: Any
    ):
        """
        Initialize Review Scorer

        Args:
            review_weights: Dictionary of weight values for each review dimension
            logger: Logger interface for diagnostics
        """
        if not review_weights:
            raise ValueError("Review weights are required")
        if not logger:
            raise ValueError("Logger is required for review scorer")

        self.review_weights = review_weights
        self.logger = logger

        # Decision thresholds
        self.approval_threshold = 8.0
        self.conditional_threshold = 6.0

    def calculate_review_score(
        self,
        arch_review: Dict[str, Any],
        sprint_review: Dict[str, Any],
        quality_review: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        Calculate overall review score and decision

        WHY: Weighted combination of all review dimensions

        Args:
            arch_review: Architecture review results
            sprint_review: Sprint planning review results
            quality_review: Quality analysis results

        Returns:
            Tuple of (score, decision) where decision is "APPROVED" or "REJECTED"
        """
        arch_score = self._extract_architecture_score(arch_review)
        sprint_score = sprint_review.get('score', 5)
        quality_score = quality_review.get('score', 5)

        overall_score = self._calculate_weighted_score(
            arch_score,
            sprint_score,
            quality_score
        )

        critical_issues = self._extract_critical_issues(arch_review, quality_review)
        decision = self._make_decision(overall_score, critical_issues)

        self.logger.log(
            f"Review scores - Arch: {arch_score:.1f}, Sprint: {sprint_score:.1f}, "
            f"Quality: {quality_score:.1f}, Overall: {overall_score:.1f}",
            "INFO"
        )

        return overall_score, decision

    def _extract_architecture_score(self, arch_review: Dict[str, Any]) -> float:
        """
        Extract average architecture score from review dimensions

        WHY: Architecture review has multiple sub-scores to aggregate
        """
        if arch_review.get('status') == 'SKIPPED':
            return 7.0  # Neutral score for skipped architecture

        arch_scores = {
            k: v.get('score', 5)
            for k, v in arch_review.items()
            if isinstance(v, dict) and 'score' in v
        }

        if not arch_scores:
            return 5.0  # Default score if no architecture scores

        return sum(arch_scores.values()) / len(arch_scores)

    def _calculate_weighted_score(
        self,
        arch_score: float,
        sprint_score: float,
        quality_score: float
    ) -> float:
        """
        Calculate weighted overall score

        WHY: Different dimensions have different importance
        """
        weighted_score = (
            arch_score * self.review_weights['architecture_quality'] +
            sprint_score * self.review_weights['sprint_feasibility'] +
            quality_score * (
                self.review_weights['technical_debt'] +
                self.review_weights['scalability'] +
                self.review_weights['maintainability']
            )
        )

        return weighted_score

    def _extract_critical_issues(
        self,
        arch_review: Dict[str, Any],
        quality_review: Dict[str, Any]
    ) -> List[str]:
        """
        Extract all critical issues from reviews

        WHY: Critical issues override score-based decisions
        """
        critical_issues = []

        if arch_review.get('critical_issues'):
            critical_issues.extend(arch_review['critical_issues'])

        if quality_review.get('critical_issues'):
            critical_issues.extend(quality_review['critical_issues'])

        return critical_issues

    def _make_decision(self, overall_score: float, critical_issues: List[str]) -> str:
        """
        Make approval/rejection decision using guard clauses

        WHY: Clear decision logic based on score thresholds and critical issues

        Decision Rules:
        - Score >= 8.0: APPROVED
        - Score >= 6.0 and no critical issues: APPROVED
        - Otherwise: REJECTED
        """
        if overall_score >= self.approval_threshold:
            return "APPROVED"

        if overall_score >= self.conditional_threshold and not critical_issues:
            return "APPROVED"

        return "REJECTED"
