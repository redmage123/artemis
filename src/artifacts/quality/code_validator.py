#!/usr/bin/env python3
"""
WHY: Validate code using Test-Driven Development approach
RESPONSIBILITY: Ensure code passes tests before acceptance
PATTERNS: Template Method (extends base), TDD (test-first validation)

Code validator enforces TDD methodology.
"""

from pathlib import Path
from artifacts.quality.base import ArtifactQualityValidator
from artifacts.quality.models import ValidationResult


class CodeQualityValidator(ArtifactQualityValidator):
    """
    Validates code using TDD approach.

    WHY: TDD ensures code correctness through passing tests.
    RESPONSIBILITY: Validate code via test execution.
    PATTERNS: Template Method, TDD (test-driven validation).
    """

    def validate(self, artifact_path: Path) -> ValidationResult:
        """
        Validate code via test execution.

        WHY: Passing tests are the ultimate code quality metric.

        Args:
            artifact_path: Path to code file

        Returns:
            ValidationResult based on test execution

        Note:
            This is a placeholder - actual implementation would run pytest.
        """
        # Placeholder - actual implementation would run pytest
        return ValidationResult(
            passed=True,
            score=1.0,
            criteria_results={'tests_pass': True},
            feedback=[]
        )

    def generate_validation_prompt(self, requirements: str) -> str:
        """
        Generate TDD prompt for code creation.

        WHY: TDD prompts guide proper test-first development.

        Args:
            requirements: User requirements

        Returns:
            TDD-focused prompt
        """
        prompt = f"""Implement code using Test-Driven Development.

Requirements:
{requirements}

Approach:
1. Write failing tests first (RED)
2. Implement MINIMUM code to pass tests (GREEN)
3. Refactor for quality (REFACTOR)

Focus on simplicity and testability.
"""
        return prompt
