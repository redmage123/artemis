#!/usr/bin/env python3
"""
WHY: Define validation data models and enums for type safety and clarity.

RESPONSIBILITY: Provides core data structures for validation stages, results, and
error tracking throughout the validation pipeline.

PATTERNS:
- Dataclass pattern for immutable data structures
- Enum pattern for type-safe stage definitions
- __str__ override for human-readable output
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ValidationStage(Enum):
    """
    WHY: Type-safe enumeration of code generation validation stages.

    Each stage represents a discrete checkpoint in the code generation process
    where validation rules apply.
    """
    IMPORTS = "imports"
    SIGNATURE = "signature"
    DOCSTRING = "docstring"
    BODY = "body"
    TESTS = "tests"
    FULL_CODE = "full_code"


class ValidationSeverity(Enum):
    """
    WHY: Type-safe severity levels for validation failures.

    Enables prioritization and filtering of validation issues.
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class StageValidationResult:
    """
    WHY: Encapsulate validation results with structured feedback.

    RESPONSIBILITY: Hold validation outcome, individual check results,
    feedback messages, and actionable suggestions.

    Attributes:
        stage: The validation stage that was executed
        passed: Overall pass/fail status
        checks: Dictionary of individual check results (check_name -> bool)
        feedback: Human-readable feedback messages
        severity: Issue severity level
        suggestion: Optional actionable suggestion for fixes
    """
    stage: ValidationStage
    passed: bool
    checks: Dict[str, bool]
    feedback: List[str]
    severity: str
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Return human-readable status summary."""
        status = "✅" if self.passed else "❌"
        failed = [k for k, v in self.checks.items() if not v]

        if not failed:
            return f"{status} {self.stage.value}"

        return f"{status} {self.stage.value}: {len(failed)} issues"

    def get_failed_checks(self) -> List[str]:
        """
        WHY: Extract failed checks for targeted error reporting.

        Returns:
            List of check names that failed
        """
        return [check_name for check_name, passed in self.checks.items() if not passed]

    def has_critical_failures(self) -> bool:
        """
        WHY: Quick check for critical validation failures.

        Returns:
            True if any critical severity issues exist
        """
        return self.severity == ValidationSeverity.CRITICAL.value and not self.passed


@dataclass
class ValidationContext:
    """
    WHY: Encapsulate contextual information for validation.

    RESPONSIBILITY: Provide validators with task-specific context like
    required imports, expected methods, and framework constraints.

    Attributes:
        required_imports: List of imports that must be present
        expected_methods: List of methods that should be used
        framework: Target framework (e.g., 'flask', 'django')
        custom_rules: Additional validation rules
    """
    required_imports: Optional[List[str]] = None
    expected_methods: Optional[List[str]] = None
    framework: Optional[str] = None
    custom_rules: Optional[Dict] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> 'ValidationContext':
        """
        WHY: Factory method for creating context from dictionary.

        Args:
            data: Dictionary with context data

        Returns:
            ValidationContext instance
        """
        if not data:
            return cls()

        return cls(
            required_imports=data.get('required_imports'),
            expected_methods=data.get('expected_methods'),
            framework=data.get('framework'),
            custom_rules=data.get('custom_rules')
        )


@dataclass
class ValidationSummary:
    """
    WHY: Aggregate validation statistics for reporting.

    RESPONSIBILITY: Summarize validation history with pass/fail rates
    and stage-specific breakdowns.

    Attributes:
        total_validations: Total number of validation runs
        passed: Number of successful validations
        failed: Number of failed validations
        pass_rate: Success rate as float (0.0 to 1.0)
        by_stage: Stage-specific statistics
        history: Complete validation history
    """
    total_validations: int
    passed: int
    failed: int
    pass_rate: float
    by_stage: Dict[str, Dict[str, int]]
    history: List[StageValidationResult]

    def get_stage_pass_rate(self, stage: ValidationStage) -> float:
        """
        WHY: Calculate pass rate for specific stage.

        Args:
            stage: Validation stage to calculate rate for

        Returns:
            Pass rate as float (0.0 to 1.0)
        """
        stage_name = stage.value

        if stage_name not in self.by_stage:
            return 0.0

        stats = self.by_stage[stage_name]
        total = stats['passed'] + stats['failed']

        if total == 0:
            return 0.0

        return stats['passed'] / total
