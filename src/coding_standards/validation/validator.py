#!/usr/bin/env python3
"""
WHY: Validate code against claude.md standards
RESPONSIBILITY: Orchestrate scanning, filtering, and formatting
PATTERNS: Facade (simplified API), Composition (scanner, filter, formatter)

Code standards validator provides pipeline integration for quality checks.
"""

from pathlib import Path
from typing import List, Optional
from code_standards_scanner import CodeStandardsScanner
from coding_standards.validation.models import ValidationResult
from coding_standards.validation.severity_filter import SeverityFilter
from coding_standards.validation.formatter import ViolationFormatter


class CodeStandardsValidator:
    """
    Validates code against claude.md standards.

    WHY: Provides clean interface for Artemis stages to check code quality.
    RESPONSIBILITY: Orchestrate scanning, filtering, and reporting.
    PATTERNS: Facade, Composition.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize validator.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose

        # Initialize components (Composition pattern)
        self.severity_filter = SeverityFilter()
        self.formatter = ViolationFormatter()

    def validate_code_standards(
        self,
        code_dir: str,
        severity_threshold: str = "warning",
        exclude_dirs: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate code directory against claude.md standards.

        WHY: Programmatic code quality checks for pipeline integration.

        Args:
            code_dir: Directory to scan
            severity_threshold: Minimum severity ("info", "warning", "critical")
            exclude_dirs: Additional directories to exclude

        Returns:
            ValidationResult with violation details

        Example:
            >>> validator = CodeStandardsValidator()
            >>> result = validator.validate_code_standards("src", "warning")
            >>> result.is_valid
            True
        """
        # Guard clause - directory must exist
        if not Path(code_dir).exists():
            return self._create_error_result(f"Directory not found: {code_dir}")

        # Setup exclusions
        exclude_set = {'.venv', '__pycache__', '.git', 'node_modules', '.artemis_data'}
        if exclude_dirs:
            exclude_set.update(exclude_dirs)

        # Create scanner and scan
        scanner = CodeStandardsScanner(code_dir, exclude_set)
        violations_by_type = scanner.scan_codebase()

        # Filter by severity
        filtered_violations = self.severity_filter.filter_by_severity(
            violations_by_type,
            severity_threshold
        )

        # Format violations
        violation_list = self.formatter.format_as_dicts(filtered_violations)

        # Determine validity
        is_valid = len(violation_list) == 0

        # Create summary
        summary = self.formatter.create_summary(
            scanner.files_scanned,
            violation_list,
            severity_threshold
        )

        return ValidationResult(
            is_valid=is_valid,
            violation_count=len(violation_list),
            violations=violation_list,
            files_scanned=scanner.files_scanned,
            summary=summary
        )

    def validate_generated_code(
        self,
        code: str,
        file_name: str = "generated.py"
    ) -> ValidationResult:
        """
        Validate a single code string against standards.

        WHY: Allows validation of AI-generated code before writing to disk.

        Args:
            code: Python code as string
            file_name: Filename for reporting purposes

        Returns:
            ValidationResult with violation details
        """
        # Create temp file for scanning
        temp_dir = Path("/tmp/artemis_code_scan")
        temp_dir.mkdir(exist_ok=True)

        temp_file = temp_dir / file_name
        temp_file.write_text(code)

        try:
            result = self.validate_code_standards(
                code_dir=str(temp_dir),
                severity_threshold="critical"
            )
            return result
        finally:
            # Cleanup
            temp_file.unlink(missing_ok=True)

    def get_violation_summary_for_report(
        self,
        violations: List[dict]
    ) -> str:
        """
        Format violations for inclusion in code review report.

        WHY: Code review stage needs markdown-formatted violations.

        Args:
            violations: List of violation dicts from ValidationResult

        Returns:
            Formatted markdown string
        """
        return self.formatter.format_as_markdown_report(violations)

    def _create_error_result(self, error_message: str) -> ValidationResult:
        """Create error result"""
        return ValidationResult(
            is_valid=False,
            violation_count=0,
            violations=[],
            files_scanned=0,
            summary=f"❌ Error: {error_message}"
        )
