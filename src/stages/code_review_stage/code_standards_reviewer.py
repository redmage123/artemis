#!/usr/bin/env python3
"""
Code Standards Reviewer for Pipeline Integration

WHY: Integrate claude.md code standards validation into code review workflow
RESPONSIBILITY: Validate generated code against claude.md standards
PATTERNS: Adapter Pattern, Single Responsibility, Guard Clauses

Validates code for:
- Nested if statements (max 1 level)
- elif chains (should use dispatch tables)
- TODO/FIXME comments
- Other claude.md violations
"""

from typing import Dict, List, Optional
from pathlib import Path

from artemis_stage_interface import LoggerInterface
from coding_standards.validation import CodeStandardsValidator, ValidationResult


class CodeStandardsReviewer:
    """
    Adapter for CodeStandardsValidator in pipeline workflow.

    WHY: Provide code review stage-compatible interface for code standards
    RESPONSIBILITY: Validate developer code against claude.md standards
    PATTERNS: Adapter Pattern, Facade Pattern
    """

    def __init__(
        self,
        logger: LoggerInterface,
        severity_threshold: str = "warning",
        enabled: bool = True
    ):
        """
        Initialize code standards reviewer.

        Args:
            logger: Logger interface
            severity_threshold: Minimum severity ("info", "warning", "critical")
            enabled: Whether code standards checking is enabled
        """
        self.logger = logger
        self.severity_threshold = severity_threshold
        self.enabled = enabled
        self.validator = CodeStandardsValidator(verbose=False)

    def review_developer_code(
        self,
        developer_name: str,
        code_directory: str
    ) -> Dict:
        """
        Review developer code for claude.md standards violations.

        WHY: Main entry point for code standards review
        RESPONSIBILITY: Execute validation and format results for pipeline

        Args:
            developer_name: Name of developer being reviewed
            code_directory: Path to developer's code output

        Returns:
            Dict with review results:
            {
                "enabled": bool,
                "passed": bool,
                "violation_count": int,
                "violations": List[dict],
                "severity_threshold": str,
                "summary": str
            }
        """
        # Guard: Code standards checking disabled
        if not self.enabled:
            return self._create_disabled_result()

        # Guard: Directory doesn't exist
        if not Path(code_directory).exists():
            return self._create_error_result(
                f"Code directory not found: {code_directory}"
            )

        self.logger.log(
            f"  📋 Validating code standards for {developer_name}...",
            "INFO"
        )

        # Execute validation
        validation_result = self.validator.validate_code_standards(
            code_dir=code_directory,
            severity_threshold=self.severity_threshold
        )

        # Format result for pipeline
        result = self._format_result(validation_result, developer_name)

        # Log summary
        self._log_review_summary(result, developer_name)

        return result

    def _format_result(
        self,
        validation_result: ValidationResult,
        developer_name: str
    ) -> Dict:
        """
        Format validation result for pipeline consumption.

        WHY: Separate formatting logic
        RESPONSIBILITY: Transform ValidationResult to pipeline format
        PATTERN: Adapter Pattern
        """
        return {
            "enabled": True,
            "passed": validation_result.is_valid,
            "violation_count": validation_result.violation_count,
            "violations": validation_result.violations,
            "files_scanned": validation_result.files_scanned,
            "severity_threshold": self.severity_threshold,
            "summary": validation_result.summary,
            "developer": developer_name
        }

    def _create_disabled_result(self) -> Dict:
        """Create result when code standards checking is disabled."""
        return {
            "enabled": False,
            "passed": True,
            "violation_count": 0,
            "violations": [],
            "files_scanned": 0,
            "severity_threshold": self.severity_threshold,
            "summary": "Code standards validation disabled"
        }

    def _create_error_result(self, error_message: str) -> Dict:
        """Create error result"""
        return {
            "enabled": True,
            "passed": False,
            "violation_count": 0,
            "violations": [],
            "files_scanned": 0,
            "severity_threshold": self.severity_threshold,
            "summary": f"Error: {error_message}",
            "error": error_message
        }

    def _log_review_summary(self, result: Dict, developer_name: str) -> None:
        """
        Log code standards review summary.

        WHY: Provide visibility into validation results
        RESPONSIBILITY: Log appropriate message based on result
        PATTERN: Guard clauses for different result types
        """
        # Guard: Disabled
        if not result["enabled"]:
            return

        # Guard: Error
        if "error" in result:
            self.logger.log(
                f"  ⚠️  Code standards check failed: {result['error']}",
                "WARNING"
            )
            return

        # Log based on pass/fail
        if result["passed"]:
            self.logger.log(
                f"  ✅ Code standards: PASSED "
                f"({result['files_scanned']} files scanned)",
                "SUCCESS"
            )
        else:
            self.logger.log(
                f"  ❌ Code standards: {result['violation_count']} "
                f"violation(s) found in {developer_name}'s code",
                "WARNING"
            )

            # Log sample violations
            violations = result["violations"]
            sample_size = min(3, len(violations))

            for violation in violations[:sample_size]:
                self.logger.log(
                    f"     - {violation['file']}:{violation['line']} "
                    f"[{violation['severity']}] {violation['message']}",
                    "WARNING"
                )

            if len(violations) > sample_size:
                remaining = len(violations) - sample_size
                self.logger.log(
                    f"     ... and {remaining} more violation(s)",
                    "WARNING"
                )

    def format_violations_for_report(
        self,
        violations: List[dict]
    ) -> str:
        """
        Format violations for inclusion in code review report.

        WHY: Code review reports need markdown-formatted violations
        RESPONSIBILITY: Convert violations to markdown

        Args:
            violations: List of violation dictionaries

        Returns:
            Markdown formatted string
        """
        # Guard: No violations
        if not violations:
            return "✅ No code standards violations detected."

        lines = [
            "## Code Standards Violations",
            "",
            f"Found {len(violations)} violation(s):",
            ""
        ]

        # Group violations by severity
        by_severity = {}
        for v in violations:
            severity = v.get('severity', 'unknown')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(v)

        # Format by severity
        for severity in ['critical', 'warning', 'info']:
            # Guard: No violations at this severity
            if severity not in by_severity:
                continue

            severity_violations = by_severity[severity]
            emoji = {'critical': '🔴', 'warning': '⚠️', 'info': 'ℹ️'}.get(severity, '•')

            lines.append(f"### {emoji} {severity.capitalize()} ({len(severity_violations)})")
            lines.append("")

            for v in severity_violations:
                file_path = v.get('file', 'unknown')
                line_num = v.get('line', '?')
                message = v.get('message', 'Unknown violation')

                lines.append(f"- **{file_path}:{line_num}**: {message}")

                # Add context if available
                context = v.get('context')
                if context:
                    lines.append(f"  ```python")
                    lines.append(f"  {context}")
                    lines.append(f"  ```")

            lines.append("")

        return "\n".join(lines)
