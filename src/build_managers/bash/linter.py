#!/usr/bin/env python3
"""
Bash Manager - Shellcheck Linter

WHY: Separate linting logic from orchestration for Single Responsibility
RESPONSIBILITY: Execute shellcheck and parse results
PATTERNS: Command Pattern, Strategy Pattern, Guard Clauses

This module wraps shellcheck static analysis tool, providing structured
results and error handling for shell script quality checks.
"""

from pathlib import Path
from typing import List, Callable, Optional
import subprocess
import logging
import re

from .models import ShellScript, LintResult, QualityCheckConfig


class ShellcheckLinter:
    """
    Shellcheck static analysis wrapper.

    WHY: Single Responsibility - only concerned with linting
    RESPONSIBILITY: Execute shellcheck and parse output
    PATTERNS: Command Pattern, Guard Clauses, Result Pattern
    """

    def __init__(
        self,
        config: QualityCheckConfig,
        execute_command: Callable[[List[str]], subprocess.CompletedProcess],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize linter.

        WHY: Dependency Injection for testability
        PATTERNS: Dependency Injection, Strategy Pattern

        Args:
            config: Quality check configuration
            execute_command: Command executor (injected for testing)
            logger: Logger instance
        """
        self.config = config
        self.execute_command = execute_command
        self.logger = logger or logging.getLogger(__name__)

    def lint_script(self, script: ShellScript) -> LintResult:
        """
        Lint a single shell script.

        WHY: Single script processing for granular control
        RESPONSIBILITY: Execute shellcheck on one script
        PATTERNS: Guard Clauses, Result Pattern

        Args:
            script: Script to lint

        Returns:
            LintResult with outcome
        """
        # Guard: Check if shellcheck is enabled
        if not self.config.enable_shellcheck:
            self.logger.debug(f"Shellcheck disabled, skipping {script.name}")
            return self._create_skipped_result(script)

        # Guard: Validate script exists
        if not script.path.exists():
            self.logger.warning(f"Script not found: {script.path}")
            return self._create_error_result(
                script,
                f"File not found: {script.path}"
            )

        # Build shellcheck command
        cmd = self.config.get_shellcheck_args(script.path)

        try:
            # Execute shellcheck
            self.logger.debug(f"Running: {' '.join(cmd)}")
            result = self.execute_command(cmd)

            # Parse result
            return self._parse_result(script, result)

        except subprocess.TimeoutExpired:
            self.logger.error(f"Shellcheck timeout for {script.name}")
            return self._create_error_result(
                script,
                "Shellcheck execution timeout"
            )

        except Exception as e:
            self.logger.error(f"Shellcheck failed for {script.name}: {e}")
            return self._create_error_result(
                script,
                str(e)
            )

    def lint_scripts(self, scripts: List[ShellScript]) -> List[LintResult]:
        """
        Lint multiple scripts.

        WHY: Batch processing with individual results
        RESPONSIBILITY: Orchestrate multiple lint operations
        PATTERNS: Map Pattern, Fail-Fast avoidance

        Args:
            scripts: Scripts to lint

        Returns:
            List of LintResults (one per script)
        """
        # Guard: Empty list check
        if not scripts:
            self.logger.info("No scripts to lint")
            return []

        results: List[LintResult] = []

        self.logger.info(f"Linting {len(scripts)} script(s)...")

        # Lint each script (don't fail-fast, collect all results)
        for script in scripts:
            result = self.lint_script(script)
            results.append(result)

            # Log individual results
            if result.passed:
                self.logger.debug(f"✓ {script.name}")
            else:
                self.logger.warning(f"✗ {script.name}: {len(result.errors)} issue(s)")

        # Summary
        passed_count = sum(1 for r in results if r.passed)
        self.logger.info(
            f"Linting complete: {passed_count}/{len(results)} passed"
        )

        return results

    def all_passed(self, results: List[LintResult]) -> bool:
        """
        Check if all lint results passed.

        WHY: Simple predicate for orchestration logic
        RESPONSIBILITY: Aggregate result status
        PATTERNS: Predicate Pattern

        Args:
            results: Lint results to check

        Returns:
            True if all passed
        """
        return all(r.passed for r in results)

    def _parse_result(
        self,
        script: ShellScript,
        result: subprocess.CompletedProcess
    ) -> LintResult:
        """
        Parse shellcheck output.

        WHY: Centralize result parsing logic
        RESPONSIBILITY: Convert subprocess result to LintResult
        PATTERNS: Factory Method, Parser Pattern

        Args:
            script: Script that was linted
            result: Subprocess result

        Returns:
            Structured LintResult
        """
        output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout
        passed = result.returncode == 0

        # Parse errors and warnings from output
        errors, warnings = self._parse_issues(output)

        return LintResult(
            script=script,
            passed=passed,
            output=output,
            exit_code=result.returncode,
            errors=errors,
            warnings=warnings
        )

    def _parse_issues(self, output: str) -> tuple[List[str], List[str]]:
        """
        Parse shellcheck issues from output.

        WHY: Extract structured data from text output
        RESPONSIBILITY: Categorize issues by severity
        PATTERNS: Parser Pattern, Regular Expressions

        Args:
            output: Shellcheck output text

        Returns:
            Tuple of (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Shellcheck format: file:line:col: level: message [SC####]
        # Example: script.sh:10:5: warning: Double quote to prevent globbing [SC2086]
        pattern = r'^.*?:(\d+):(\d+):\s+(\w+):\s+(.+)$'

        for line in output.splitlines():
            match = re.match(pattern, line)
            if not match:
                continue

            line_num, col_num, level, message = match.groups()
            issue = f"Line {line_num}:{col_num} [{level}] {message}"

            # Categorize by level
            if level.lower() in ('error', 'critical'):
                errors.append(issue)
            else:
                warnings.append(issue)

        return errors, warnings

    def _create_skipped_result(self, script: ShellScript) -> LintResult:
        """
        Create result for skipped script.

        WHY: Consistent result objects even for skipped scripts
        RESPONSIBILITY: Factory method for skipped results
        PATTERNS: Factory Method, Null Object Pattern

        Args:
            script: Script that was skipped

        Returns:
            LintResult indicating skip
        """
        return LintResult(
            script=script,
            passed=True,  # Skipped = passing
            output="Shellcheck disabled",
            exit_code=0,
            errors=[],
            warnings=[]
        )

    def _create_error_result(self, script: ShellScript, error: str) -> LintResult:
        """
        Create result for script with errors.

        WHY: Consistent error handling
        RESPONSIBILITY: Factory method for error results
        PATTERNS: Factory Method

        Args:
            script: Script with error
            error: Error message

        Returns:
            LintResult indicating failure
        """
        return LintResult(
            script=script,
            passed=False,
            output=error,
            exit_code=1,
            errors=[error],
            warnings=[]
        )


__all__ = [
    'ShellcheckLinter'
]
