#!/usr/bin/env python3
"""
Bash Manager - Shfmt Formatter

WHY: Separate formatting logic from orchestration for Single Responsibility
RESPONSIBILITY: Execute shfmt and parse results
PATTERNS: Command Pattern, Strategy Pattern, Guard Clauses

This module wraps shfmt shell script formatter, providing structured
results for format checking and validation.
"""

from pathlib import Path
from typing import List, Callable, Optional
import subprocess
import logging

from .models import ShellScript, FormatResult, QualityCheckConfig


class ShfmtFormatter:
    """
    Shfmt shell script formatter wrapper.

    WHY: Single Responsibility - only concerned with formatting
    RESPONSIBILITY: Execute shfmt and parse output
    PATTERNS: Command Pattern, Guard Clauses, Result Pattern
    """

    def __init__(
        self,
        config: QualityCheckConfig,
        execute_command: Callable[[List[str]], subprocess.CompletedProcess],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize formatter.

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

    def check_format(self, script: ShellScript) -> FormatResult:
        """
        Check if script is properly formatted.

        WHY: Single script processing for granular control
        RESPONSIBILITY: Execute shfmt on one script (check mode)
        PATTERNS: Guard Clauses, Result Pattern

        Args:
            script: Script to check

        Returns:
            FormatResult with outcome
        """
        # Guard: Check if shfmt is enabled
        if not self.config.enable_shfmt:
            self.logger.debug(f"Shfmt disabled, skipping {script.name}")
            return self._create_skipped_result(script)

        # Guard: Validate script exists
        if not script.path.exists():
            self.logger.warning(f"Script not found: {script.path}")
            return self._create_error_result(
                script,
                f"File not found: {script.path}"
            )

        # Build shfmt command
        cmd = self._build_command(script.path)

        try:
            # Execute shfmt
            self.logger.debug(f"Running: {' '.join(cmd)}")
            result = self.execute_command(cmd)

            # Parse result
            return self._parse_result(script, result)

        except subprocess.TimeoutExpired:
            self.logger.error(f"Shfmt timeout for {script.name}")
            return self._create_error_result(
                script,
                "Shfmt execution timeout"
            )

        except Exception as e:
            self.logger.error(f"Shfmt failed for {script.name}: {e}")
            return self._create_error_result(
                script,
                str(e)
            )

    def check_formats(self, scripts: List[ShellScript]) -> List[FormatResult]:
        """
        Check formatting for multiple scripts.

        WHY: Batch processing with individual results
        RESPONSIBILITY: Orchestrate multiple format checks
        PATTERNS: Map Pattern, Fail-Fast avoidance

        Args:
            scripts: Scripts to check

        Returns:
            List of FormatResults (one per script)
        """
        # Guard: Empty list check
        if not scripts:
            self.logger.info("No scripts to format-check")
            return []

        results: List[FormatResult] = []

        self.logger.info(f"Checking format for {len(scripts)} script(s)...")

        # Check each script (don't fail-fast, collect all results)
        for script in scripts:
            result = self.check_format(script)
            results.append(result)

            # Log individual results
            if result.formatted:
                self.logger.debug(f"✓ {script.name}")
            else:
                self.logger.warning(f"✗ {script.name}: needs formatting")

        # Summary
        formatted_count = sum(1 for r in results if r.formatted)
        self.logger.info(
            f"Format check complete: {formatted_count}/{len(results)} formatted"
        )

        return results

    def all_formatted(self, results: List[FormatResult]) -> bool:
        """
        Check if all format results passed.

        WHY: Simple predicate for orchestration logic
        RESPONSIBILITY: Aggregate result status
        PATTERNS: Predicate Pattern

        Args:
            results: Format results to check

        Returns:
            True if all properly formatted
        """
        return all(r.formatted for r in results)

    def format_script(self, script: ShellScript) -> bool:
        """
        Format a script in-place (write mode).

        WHY: Support auto-formatting workflows
        RESPONSIBILITY: Execute shfmt in write mode
        PATTERNS: Command Pattern, Guard Clauses

        Args:
            script: Script to format

        Returns:
            True if formatting succeeded
        """
        # Guard: Check if shfmt is enabled
        if not self.config.enable_shfmt:
            self.logger.debug(f"Shfmt disabled, skipping {script.name}")
            return True

        # Guard: Validate script exists
        if not script.path.exists():
            self.logger.warning(f"Script not found: {script.path}")
            return False

        # Build write-mode command
        cmd = self._build_command(script.path, write_mode=True)

        try:
            # Execute shfmt
            self.logger.info(f"Formatting {script.name}...")
            result = self.execute_command(cmd)
            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Failed to format {script.name}: {e}")
            return False

    def _build_command(self, script_path: Path, write_mode: bool = False) -> List[str]:
        """
        Build shfmt command.

        WHY: Centralize command construction
        RESPONSIBILITY: Translate config to CLI command
        PATTERNS: Builder Pattern

        Args:
            script_path: Script to format
            write_mode: If True, write changes; if False, show diff

        Returns:
            Command arguments list
        """
        cmd = ["shfmt"]

        if write_mode:
            cmd.append("-w")  # Write mode
        else:
            # Use config to get diff mode args
            cmd.extend(self.config.get_shfmt_args())

        cmd.append(str(script_path))

        return cmd

    def _parse_result(
        self,
        script: ShellScript,
        result: subprocess.CompletedProcess
    ) -> FormatResult:
        """
        Parse shfmt output.

        WHY: Centralize result parsing logic
        RESPONSIBILITY: Convert subprocess result to FormatResult
        PATTERNS: Factory Method, Parser Pattern

        Args:
            script: Script that was checked
            result: Subprocess result

        Returns:
            Structured FormatResult
        """
        output = result.stdout.decode() if isinstance(result.stdout, bytes) else result.stdout

        # Shfmt returns 0 if no formatting needed, non-zero if changes detected
        formatted = result.returncode == 0
        diff = output if not formatted else ""

        return FormatResult(
            script=script,
            formatted=formatted,
            diff=diff,
            exit_code=result.returncode
        )

    def _create_skipped_result(self, script: ShellScript) -> FormatResult:
        """
        Create result for skipped script.

        WHY: Consistent result objects even for skipped scripts
        RESPONSIBILITY: Factory method for skipped results
        PATTERNS: Factory Method, Null Object Pattern

        Args:
            script: Script that was skipped

        Returns:
            FormatResult indicating skip
        """
        return FormatResult(
            script=script,
            formatted=True,  # Skipped = passing
            diff="",
            exit_code=0
        )

    def _create_error_result(self, script: ShellScript, error: str) -> FormatResult:
        """
        Create result for script with errors.

        WHY: Consistent error handling
        RESPONSIBILITY: Factory method for error results
        PATTERNS: Factory Method

        Args:
            script: Script with error
            error: Error message

        Returns:
            FormatResult indicating failure
        """
        return FormatResult(
            script=script,
            formatted=False,
            diff=error,
            exit_code=1
        )


__all__ = [
    'ShfmtFormatter'
]
