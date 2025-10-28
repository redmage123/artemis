#!/usr/bin/env python3
"""
Configuration Validation Models

WHY: Encapsulates validation check results and reports with type safety

RESPONSIBILITY: Define data structures for validation results and reports

PATTERNS: Dataclass pattern for immutable value objects
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationResult:
    """
    Result of a validation check

    WHY: Encapsulates validation check results with context

    Attributes:
        check_name: Name of the validation check
        passed: Whether the check passed
        message: Human-readable message
        severity: error, warning, or info
        fix_suggestion: Optional suggestion for fixing failures
    """
    check_name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    fix_suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    """
    Complete validation report

    WHY: Aggregates all validation results for comprehensive reporting

    Attributes:
        overall_status: pass, warning, or fail
        total_checks: Total number of checks performed
        passed: Number of checks that passed
        warnings: Number of warnings
        errors: Number of errors
        results: List of all validation results
    """
    overall_status: str  # pass, warning, fail
    total_checks: int
    passed: int
    warnings: int
    errors: int
    results: List[ValidationResult] = field(default_factory=list)
