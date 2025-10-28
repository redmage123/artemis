#!/usr/bin/env python3
"""
WHY: Value objects for UI/UX evaluation results
RESPONSIBILITY: Define immutable data structures for evaluation outcomes
PATTERNS: Value Object pattern for type-safe, immutable results

This module contains data classes representing UI/UX evaluation results.
All classes are frozen (immutable) to ensure data integrity throughout the pipeline.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class DeveloperEvaluation:
    """
    WHY: Encapsulates complete UI/UX evaluation for a single developer
    RESPONSIBILITY: Immutable evaluation result container
    PATTERNS: Value Object - immutable, self-documenting, type-safe

    Benefits:
    - Immutable result object prevents accidental modification
    - Type-safe access to all evaluation fields
    - Self-documenting structure
    - No speculative generality (only implemented features)

    Attributes:
        developer: Developer name
        task_title: Task being evaluated
        evaluation_status: Overall status ("PASS", "NEEDS_IMPROVEMENT", "FAIL")
        ux_score: Numeric score 0-100
        accessibility_issues: Count of WCAG accessibility issues
        wcag_aa_compliance: Whether WCAG AA standards are met
        accessibility_details: Detailed accessibility analysis
        accessibility_issues_list: List of specific accessibility issues
        ux_issues: Total UX issues count
        ux_issues_details: List of specific UX issues
        gdpr_compliance: GDPR compliance status dict
        gdpr_issues: Count of GDPR compliance issues
        gdpr_issues_list: List of specific GDPR issues
    """
    developer: str
    task_title: str
    evaluation_status: str  # "PASS", "NEEDS_IMPROVEMENT", "FAIL"
    ux_score: int  # 0-100

    # WCAG Accessibility results
    accessibility_issues: int
    wcag_aa_compliance: bool
    accessibility_details: Dict
    accessibility_issues_list: List[Dict]

    # UX issues
    ux_issues: int
    ux_issues_details: List[Dict]

    # GDPR compliance results
    gdpr_compliance: Dict
    gdpr_issues: int
    gdpr_issues_list: List[Dict]

    def to_dict(self) -> Dict:
        """
        WHY: Convert to dictionary for pipeline context and serialization
        RESPONSIBILITY: Provide dict representation
        PATTERNS: Serialization pattern

        Returns:
            Dictionary representation of evaluation
        """
        return {
            "developer": self.developer,
            "task_title": self.task_title,
            "evaluation_status": self.evaluation_status,
            "ux_score": self.ux_score,
            "accessibility_issues": self.accessibility_issues,
            "wcag_aa_compliance": self.wcag_aa_compliance,
            "accessibility_details": self.accessibility_details,
            "accessibility_issues_list": self.accessibility_issues_list,
            "ux_issues": self.ux_issues,
            "ux_issues_details": self.ux_issues_details,
            "gdpr_compliance": self.gdpr_compliance,
            "gdpr_issues": self.gdpr_issues,
            "gdpr_issues_list": self.gdpr_issues_list
        }
