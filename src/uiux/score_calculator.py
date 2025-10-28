#!/usr/bin/env python3
"""
WHY: Calculate UX scores and determine evaluation status
RESPONSIBILITY: Score calculation and status determination logic
PATTERNS: Strategy pattern for configurable scoring, Guard clauses for clean control flow

This module handles all scoring and status determination for UI/UX evaluations.
Scores are calculated based on configurable deduction values to avoid magic numbers.
"""

from typing import Dict, Any, Optional


class ScoreCalculator:
    """
    WHY: Centralized scoring logic for UI/UX evaluations
    RESPONSIBILITY: Calculate UX scores and determine pass/fail status
    PATTERNS: Strategy pattern with configurable deductions

    Benefits:
    - No magic numbers (all values from configuration)
    - Testable scoring logic
    - Consistent evaluation criteria
    - Easy to adjust thresholds
    """

    def __init__(self, config: Optional[Any] = None):
        """
        WHY: Initialize with configurable thresholds
        RESPONSIBILITY: Load configuration with sensible defaults

        Args:
            config: Optional configuration agent
        """
        self._load_config(config)

    def _load_config(self, config: Optional[Any]):
        """
        WHY: Load configuration with sensible defaults
        RESPONSIBILITY: Set up scoring deductions and thresholds
        PATTERNS: Configuration pattern with defaults

        Args:
            config: Optional configuration agent
        """
        if config:
            # Load from ConfigurationAgent
            self.score_deductions = {
                'wcag_critical': config.get('uiux.score_deductions.wcag_critical', 20),
                'wcag_serious': config.get('uiux.score_deductions.wcag_serious', 10),
                'wcag_moderate': config.get('uiux.score_deductions.wcag_moderate', 5),
                'gdpr_critical': config.get('uiux.score_deductions.gdpr_critical', 20),
                'gdpr_high': config.get('uiux.score_deductions.gdpr_high', 10),
                'gdpr_medium': config.get('uiux.score_deductions.gdpr_medium', 5),
            }
            self.critical_accessibility_threshold = config.get(
                'uiux.thresholds.critical_accessibility_issues', 5
            )
        else:
            # Sensible defaults if no config
            self.score_deductions = {
                'wcag_critical': 20,
                'wcag_serious': 10,
                'wcag_moderate': 5,
                'gdpr_critical': 20,
                'gdpr_high': 10,
                'gdpr_medium': 5,
            }
            self.critical_accessibility_threshold = 5

    def calculate_ux_score(self, wcag_results: Dict, gdpr_results: Dict) -> int:
        """
        WHY: Calculate UX score based on issue severity
        RESPONSIBILITY: Compute 0-100 score from evaluation results
        PATTERNS: Calculation with configured deductions

        Uses configuration for deductions (NO MAGIC NUMBERS!)

        Args:
            wcag_results: WCAG evaluation results with issue counts
            gdpr_results: GDPR evaluation results with issue counts

        Returns:
            UX score (0-100)
        """
        # Get deductions from configuration
        deductions = self.score_deductions

        # Start at 100 and deduct points for issues
        ux_score = 100
        ux_score -= wcag_results.get('critical_count', 0) * deductions['wcag_critical']
        ux_score -= wcag_results.get('serious_count', 0) * deductions['wcag_serious']
        ux_score -= wcag_results.get('moderate_count', 0) * deductions['wcag_moderate']
        ux_score -= gdpr_results.get('critical_count', 0) * deductions['gdpr_critical']
        ux_score -= gdpr_results.get('high_count', 0) * deductions['gdpr_high']
        ux_score -= gdpr_results.get('medium_count', 0) * deductions['gdpr_medium']

        return max(0, ux_score)  # Don't go below 0

    def determine_evaluation_status(
        self,
        wcag_results: Dict,
        gdpr_results: Dict,
        total_issues: int
    ) -> str:
        """
        WHY: Determine evaluation status using early returns (avoid elif chain)
        RESPONSIBILITY: Classify evaluation as PASS/NEEDS_IMPROVEMENT/FAIL
        PATTERNS: Guard clause pattern for cleaner control flow

        Args:
            wcag_results: WCAG evaluation results
            gdpr_results: GDPR evaluation results
            total_issues: Total issues count

        Returns:
            Evaluation status ("FAIL", "NEEDS_IMPROVEMENT", or "PASS")
        """
        # Guard clause: Critical issues = FAIL
        if wcag_results.get('critical_count', 0) > 0 or gdpr_results.get('critical_count', 0) > 0:
            return "FAIL"

        # Guard clause: Serious issues = NEEDS_IMPROVEMENT
        if wcag_results.get('serious_count', 0) > 0 or gdpr_results.get('high_count', 0) > 0:
            return "NEEDS_IMPROVEMENT"

        # Guard clause: No issues = PASS
        if total_issues == 0:
            return "PASS"

        # Default: Some minor issues = NEEDS_IMPROVEMENT
        return "NEEDS_IMPROVEMENT"

    def determine_stage_status(
        self,
        total_accessibility_issues: int,
        all_evaluations_pass: bool
    ) -> str:
        """
        WHY: Determine overall stage status using early returns
        RESPONSIBILITY: Classify stage result as PASS/NEEDS_IMPROVEMENT/FAIL
        PATTERNS: Guard clause pattern for cleaner control flow

        Uses configuration threshold (NO MAGIC NUMBERS!)

        Args:
            total_accessibility_issues: Total accessibility issues found
            all_evaluations_pass: Whether all evaluations passed

        Returns:
            Stage status ("PASS", "NEEDS_IMPROVEMENT", "FAIL")
        """
        # Guard clause: Too many accessibility issues = FAIL
        if total_accessibility_issues > self.critical_accessibility_threshold:
            return "FAIL"

        # Guard clause: Some evaluations didn't pass = NEEDS_IMPROVEMENT
        if not all_evaluations_pass:
            return "NEEDS_IMPROVEMENT"

        # All evaluations passed = PASS
        return "PASS"

    def get_critical_threshold(self) -> int:
        """
        WHY: Expose threshold for use in logging
        RESPONSIBILITY: Provide access to threshold value

        Returns:
            Critical accessibility issues threshold
        """
        return self.critical_accessibility_threshold
