#!/usr/bin/env python3
"""
WHY: Process critique findings to generate actionable feedback.

RESPONSIBILITY:
- Determine if code regeneration is needed
- Generate structured feedback for code improvement
- Apply threshold rules for confidence and uncertainty
- Prioritize findings by severity

PATTERNS:
- Guard Clause Pattern: Early exit on critical/error conditions
- Strategy Pattern: Different feedback strategies per severity
- Dispatch Table: Severity-to-handler mapping
"""

import logging
from typing import List, Tuple, Optional, Callable, Dict

from .models import CritiqueFinding, CritiqueSeverity, UncertaintyMetrics


class FeedbackProcessor:
    """
    WHY: Generate actionable feedback from critique analysis.

    RESPONSIBILITY:
    - Evaluate if regeneration is needed
    - Create structured feedback messages
    - Apply configurable thresholds
    - Prioritize critical issues
    """

    # Thresholds for regeneration
    HIGH_UNCERTAINTY_THRESHOLD = 7.0
    LOW_CONFIDENCE_THRESHOLD = 6.0

    def __init__(self, strict_mode: bool = False, logger: Optional[logging.Logger] = None):
        """
        Initialize feedback processor.

        Args:
            strict_mode: If True, fail on warnings
            logger: Optional logger
        """
        self.strict_mode = strict_mode
        self.logger = logger or logging.getLogger(__name__)

        # Dispatch table for severity handlers
        self._severity_handlers: Dict[CritiqueSeverity, Callable] = {
            CritiqueSeverity.CRITICAL: self._process_critical_findings,
            CritiqueSeverity.ERROR: self._process_error_findings,
            CritiqueSeverity.WARNING: self._process_warning_findings,
        }

    def should_regenerate(
        self,
        findings: List[CritiqueFinding],
        uncertainty_metrics: UncertaintyMetrics,
        confidence_score: float
    ) -> Tuple[bool, str]:
        """
        Determine if code should be regenerated.

        Args:
            findings: List of critique findings
            uncertainty_metrics: Uncertainty analysis results
            confidence_score: LLM confidence score (0-10)

        Returns:
            (should_regenerate, feedback_for_regeneration)
        """
        # Guard clause: Critical findings always require regeneration
        critical_findings = [f for f in findings if f.severity == CritiqueSeverity.CRITICAL]
        if critical_findings:
            feedback = self._process_critical_findings(critical_findings)
            return True, feedback

        # Guard clause: Error findings require regeneration
        error_findings = [f for f in findings if f.severity == CritiqueSeverity.ERROR]
        if error_findings:
            feedback = self._process_error_findings(error_findings)
            return True, feedback

        # Guard clause: High uncertainty requires regeneration
        if uncertainty_metrics.uncertainty_score > self.HIGH_UNCERTAINTY_THRESHOLD:
            feedback = self._process_high_uncertainty(uncertainty_metrics)
            return True, feedback

        # Guard clause: Low confidence requires regeneration
        if confidence_score < self.LOW_CONFIDENCE_THRESHOLD:
            feedback = f"Low confidence score ({confidence_score}/10). Review and improve code quality."
            return True, feedback

        # Guard clause: In strict mode, warnings also require regeneration
        if self.strict_mode:
            warning_findings = [f for f in findings if f.severity == CritiqueSeverity.WARNING]
            if warning_findings:
                feedback = self._process_warning_findings(warning_findings)
                return True, feedback

        return False, ""

    def _process_critical_findings(self, findings: List[CritiqueFinding]) -> str:
        """
        Generate feedback for critical findings.

        Args:
            findings: List of critical findings

        Returns:
            Formatted feedback string
        """
        feedback = "Critical issues found:\n"
        feedback += "\n".join(f"- {f.category}: {f.message}" for f in findings)
        return feedback

    def _process_error_findings(self, findings: List[CritiqueFinding]) -> str:
        """
        Generate feedback for error findings.

        Args:
            findings: List of error findings

        Returns:
            Formatted feedback string
        """
        feedback = "Errors found:\n"
        feedback += "\n".join(
            f"- {f.category}: {f.message}\n  Fix: {f.suggestion or 'See above'}"
            for f in findings
        )
        return feedback

    def _process_warning_findings(self, findings: List[CritiqueFinding]) -> str:
        """
        Generate feedback for warning findings.

        Args:
            findings: List of warning findings

        Returns:
            Formatted feedback string
        """
        # Limit to first 5 warnings to avoid overwhelming feedback
        limited_findings = findings[:5]
        feedback = "Warnings found (strict mode):\n"
        feedback += "\n".join(f"- {f.category}: {f.message}" for f in limited_findings)

        if len(findings) > 5:
            feedback += f"\n... and {len(findings) - 5} more warnings"

        return feedback

    def _process_high_uncertainty(self, metrics: UncertaintyMetrics) -> str:
        """
        Generate feedback for high uncertainty.

        Args:
            metrics: Uncertainty metrics

        Returns:
            Formatted feedback string
        """
        feedback = f"High uncertainty detected (score: {metrics.uncertainty_score:.1f}):\n"

        if metrics.placeholder_comments:
            limited_placeholders = metrics.placeholder_comments[:3]
            feedback += "- Remove placeholder comments: " + ", ".join(limited_placeholders) + "\n"

        if metrics.missing_error_handling:
            limited_errors = metrics.missing_error_handling[:3]
            feedback += "- Add error handling: " + ", ".join(limited_errors) + "\n"

        if metrics.hedging_words:
            feedback += f"- Remove hedging language ({len(metrics.hedging_words)} instances found)\n"

        if metrics.conditional_assumptions:
            feedback += f"- Clarify conditional assumptions ({len(metrics.conditional_assumptions)} found)\n"

        return feedback
