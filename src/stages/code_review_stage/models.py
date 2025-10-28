#!/usr/bin/env python3
"""
Code Review Stage - Data Models and Types

WHY: Separate data structures from business logic for better testability and clarity.
RESPONSIBILITY: Define data models for code review results, metrics, and stage output.
PATTERNS: Value Objects pattern - immutable data structures with clear semantics.

This module contains all data structures used in the code review stage,
including review results, metrics, and stage status types.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ReviewStatus(Enum):
    """
    Code review status enumeration.

    WHY: Type-safe status values prevent typos and enable exhaustive checking.
    """
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class ReviewMetrics:
    """
    Immutable review metrics value object.

    WHY: Immutable data structure prevents accidental mutations and simplifies reasoning.
    RESPONSIBILITY: Store review metrics (scores, issue counts).

    Attributes:
        review_status: Overall review status (PASS/FAIL/NEEDS_IMPROVEMENT)
        overall_score: Score from 0-100
        critical_issues: Count of critical issues found
        high_issues: Count of high priority issues found
        total_issues: Total count of all issues found
    """
    review_status: str
    overall_score: int
    critical_issues: int
    high_issues: int
    total_issues: int

    @staticmethod
    def from_dict(data: Dict) -> 'ReviewMetrics':
        """
        Create ReviewMetrics from dictionary.

        WHY: Factory method provides type-safe construction from raw data.

        Args:
            data: Dictionary with review metrics

        Returns:
            ReviewMetrics instance
        """
        return ReviewMetrics(
            review_status=data.get('review_status', 'FAIL'),
            overall_score=data.get('overall_score', 0),
            critical_issues=data.get('critical_issues', 0),
            high_issues=data.get('high_issues', 0),
            total_issues=data.get('total_issues', 0)
        )


@dataclass(frozen=True)
class DeveloperReviewResult:
    """
    Immutable developer review result value object.

    WHY: Encapsulates all review data for a single developer implementation.
    RESPONSIBILITY: Store complete review results for one developer.

    Attributes:
        developer_name: Name of the developer
        review_result: Complete review result dictionary
        metrics: Extracted review metrics
    """
    developer_name: str
    review_result: Dict
    metrics: ReviewMetrics

    @property
    def review_status(self) -> str:
        """Get review status (convenience property)"""
        return self.metrics.review_status

    @property
    def critical_issues(self) -> int:
        """Get critical issues count (convenience property)"""
        return self.metrics.critical_issues

    @property
    def high_issues(self) -> int:
        """Get high issues count (convenience property)"""
        return self.metrics.high_issues


@dataclass(frozen=True)
class StageProgress:
    """
    Immutable stage progress value object.

    WHY: Track stage execution progress for monitoring and UI updates.
    RESPONSIBILITY: Store current progress state.

    Attributes:
        step: Current step name
        progress_percent: Progress percentage (0-100)
        current_developer: Currently processing developer (optional)
        total_developers: Total number of developers (optional)
    """
    step: str
    progress_percent: int
    current_developer: Optional[str] = None
    total_developers: Optional[int] = None

    def to_dict(self) -> Dict:
        """
        Convert to dictionary.

        WHY: Enable serialization for progress updates.

        Returns:
            Dictionary representation
        """
        result = {
            "step": self.step,
            "progress_percent": self.progress_percent
        }

        if self.current_developer:
            result["current_developer"] = self.current_developer
        if self.total_developers:
            result["total_developers"] = self.total_developers

        return result


@dataclass(frozen=True)
class CodeReviewStageResult:
    """
    Immutable code review stage result value object.

    WHY: Type-safe result structure ensures consistent return values.
    RESPONSIBILITY: Store complete stage execution results.

    Attributes:
        stage: Stage name (always "code_review")
        status: Stage status (PASS/FAIL/NEEDS_IMPROVEMENT/SKIPPED)
        reviews: List of individual review results
        total_critical_issues: Sum of critical issues across all reviews
        total_high_issues: Sum of high issues across all reviews
        all_reviews_pass: Whether all reviews passed
        implementations_reviewed: Count of implementations reviewed
        reason: Optional reason for status (used with SKIPPED)
        refactoring_suggestions: Optional refactoring suggestions text
    """
    stage: str
    status: str
    reviews: List[Dict]
    total_critical_issues: int
    total_high_issues: int
    all_reviews_pass: bool
    implementations_reviewed: int
    reason: Optional[str] = None
    refactoring_suggestions: Optional[str] = None

    def to_dict(self) -> Dict:
        """
        Convert to dictionary.

        WHY: Enable serialization for pipeline context passing.

        Returns:
            Dictionary representation
        """
        result = {
            "stage": self.stage,
            "status": self.status,
            "reviews": self.reviews,
            "total_critical_issues": self.total_critical_issues,
            "total_high_issues": self.total_high_issues,
            "all_reviews_pass": self.all_reviews_pass,
            "implementations_reviewed": self.implementations_reviewed
        }

        if self.reason:
            result["reason"] = self.reason
        if self.refactoring_suggestions:
            result["refactoring_suggestions"] = self.refactoring_suggestions

        return result

    @staticmethod
    def skipped(reason: str) -> 'CodeReviewStageResult':
        """
        Create a SKIPPED result.

        WHY: Factory method for common case of skipped review.

        Args:
            reason: Reason for skipping

        Returns:
            CodeReviewStageResult with SKIPPED status
        """
        return CodeReviewStageResult(
            stage="code_review",
            status="SKIPPED",
            reviews=[],
            total_critical_issues=0,
            total_high_issues=0,
            all_reviews_pass=True,
            implementations_reviewed=0,
            reason=reason
        )
