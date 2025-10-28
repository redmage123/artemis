#!/usr/bin/env python3
"""
Feedback Compiler - Review Feedback Aggregation

WHY: Compile actionable feedback from multiple review dimensions
RESPONSIBILITY: Aggregate architecture, sprint, and quality feedback into structured format
PATTERNS: Single Responsibility, Guard Clauses, Structured Feedback

This module:
- Aggregates feedback from all review dimensions
- Organizes feedback by category
- Generates actionable steps
- Creates human-readable summaries
"""

from typing import Dict, List, Any


class FeedbackCompiler:
    """
    Compiles actionable feedback for Architecture stage

    WHY: Provide structured, actionable feedback for revision
    RESPONSIBILITY: Aggregate and organize feedback from multiple sources
    """

    def __init__(self, logger: Any):
        """
        Initialize Feedback Compiler

        Args:
            logger: Logger interface for diagnostics
        """
        if not logger:
            raise ValueError("Logger is required for feedback compiler")

        self.logger = logger

    def compile_feedback(
        self,
        arch_review: Dict[str, Any],
        sprint_review: Dict[str, Any],
        quality_review: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compile actionable feedback from all review dimensions

        WHY: Provide structured feedback for architectural revision

        Args:
            arch_review: Architecture review results
            sprint_review: Sprint planning review results
            quality_review: Quality analysis results

        Returns:
            Dictionary with categorized feedback and actionable steps
        """
        feedback = {
            "architecture_issues": [],
            "sprint_issues": [],
            "quality_issues": [],
            "actionable_steps": []
        }

        self._extract_architecture_feedback(arch_review, feedback)
        self._extract_sprint_feedback(sprint_review, feedback)
        self._extract_quality_feedback(quality_review, feedback)

        feedback['summary'] = self._generate_feedback_summary(feedback)

        self.logger.log(
            f"Compiled feedback: {len(feedback['architecture_issues'])} arch, "
            f"{len(feedback['sprint_issues'])} sprint, "
            f"{len(feedback['quality_issues'])} quality issues",
            "INFO"
        )

        return feedback

    def _extract_architecture_feedback(
        self,
        arch_review: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> None:
        """
        Extract architecture-specific feedback

        WHY: Separate concern for architecture feedback extraction
        """
        if not arch_review:
            return

        # Extract critical issues
        critical_issues = arch_review.get('critical_issues', [])
        if critical_issues:
            feedback['architecture_issues'].extend(critical_issues)

        # Extract suggestions as actionable steps
        suggestions = arch_review.get('suggestions', [])
        if suggestions:
            feedback['actionable_steps'].extend(suggestions)

    def _extract_sprint_feedback(
        self,
        sprint_review: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> None:
        """
        Extract sprint planning feedback

        WHY: Separate concern for sprint feedback extraction
        """
        if not sprint_review:
            return

        # Extract sprint issues
        sprint_issues = sprint_review.get('issues', [])
        if sprint_issues:
            feedback['sprint_issues'].extend(sprint_issues)

    def _extract_quality_feedback(
        self,
        quality_review: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> None:
        """
        Extract quality analysis feedback

        WHY: Separate concern for quality feedback extraction
        """
        if not quality_review:
            return

        # Extract critical issues
        critical_issues = quality_review.get('critical_issues', [])
        if critical_issues:
            feedback['quality_issues'].extend(critical_issues)

        # Extract warnings
        warnings = quality_review.get('warnings', [])
        if warnings:
            feedback['quality_issues'].extend(warnings)

    def _generate_feedback_summary(self, feedback: Dict[str, Any]) -> str:
        """
        Generate human-readable feedback summary

        WHY: Provide quick overview of feedback categories

        Args:
            feedback: Feedback dictionary with categorized issues

        Returns:
            Human-readable summary string
        """
        arch_count = len(feedback['architecture_issues'])
        sprint_count = len(feedback['sprint_issues'])
        quality_count = len(feedback['quality_issues'])

        # Build summary using guard clauses
        if arch_count == 0 and sprint_count == 0 and quality_count == 0:
            return "Minor improvements needed"

        parts = []

        if arch_count > 0:
            parts.append(f"{arch_count} architecture issue(s)")

        if sprint_count > 0:
            parts.append(f"{sprint_count} sprint planning issue(s)")

        if quality_count > 0:
            parts.append(f"{quality_count} quality issue(s)")

        return f"Address: {', '.join(parts)}"
