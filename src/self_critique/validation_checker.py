#!/usr/bin/env python3
"""
WHY: Determine pass/fail status of code validation.

RESPONSIBILITY:
- Evaluate critique findings against severity thresholds
- Apply strict mode rules for warning escalation
- Determine final pass/fail status
- Consider regeneration requirements in validation

PATTERNS:
- Guard Clause Pattern: Early exit on critical conditions
- Strategy Pattern: Different validation rules for strict/lenient modes
- Single Responsibility: Only validates, doesn't generate or process
"""

import logging
from typing import List, Optional

from .models import CritiqueFinding, CritiqueSeverity


class ValidationChecker:
    """
    WHY: Determine if code passes validation based on findings.

    RESPONSIBILITY:
    - Apply severity-based validation rules
    - Handle strict mode escalation
    - Return clear pass/fail decision
    """

    def __init__(self, strict_mode: bool = False, logger: Optional[logging.Logger] = None):
        """
        Initialize validation checker.

        Args:
            strict_mode: If True, fail on warnings; if False, only fail on errors
            logger: Optional logger
        """
        self.strict_mode = strict_mode
        self.logger = logger or logging.getLogger(__name__)

    def determine_pass_fail(
        self,
        findings: List[CritiqueFinding],
        regeneration_needed: bool
    ) -> bool:
        """
        Determine if validation passed.

        Args:
            findings: List of critique findings
            regeneration_needed: Whether code needs regeneration

        Returns:
            True if validation passed, False otherwise
        """
        # Guard clause: Regeneration needed means failure
        if regeneration_needed:
            return False

        # Guard clause: Critical findings mean failure
        if self._has_critical_findings(findings):
            self.logger.warning("Validation failed: Critical findings detected")
            return False

        # Guard clause: Error findings mean failure
        if self._has_error_findings(findings):
            self.logger.warning("Validation failed: Error findings detected")
            return False

        # Guard clause: In strict mode, warnings mean failure
        if self.strict_mode and self._has_warning_findings(findings):
            self.logger.info("Validation failed: Warning findings in strict mode")
            return False

        # Otherwise validation passed
        return True

    def _has_critical_findings(self, findings: List[CritiqueFinding]) -> bool:
        """
        Check if any critical findings exist.

        Args:
            findings: List of critique findings

        Returns:
            True if critical findings present
        """
        return any(f.severity == CritiqueSeverity.CRITICAL for f in findings)

    def _has_error_findings(self, findings: List[CritiqueFinding]) -> bool:
        """
        Check if any error findings exist.

        Args:
            findings: List of critique findings

        Returns:
            True if error findings present
        """
        return any(f.severity == CritiqueSeverity.ERROR for f in findings)

    def _has_warning_findings(self, findings: List[CritiqueFinding]) -> bool:
        """
        Check if any warning findings exist.

        Args:
            findings: List of critique findings

        Returns:
            True if warning findings present
        """
        return any(f.severity == CritiqueSeverity.WARNING for f in findings)
