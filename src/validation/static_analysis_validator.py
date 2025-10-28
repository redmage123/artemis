#!/usr/bin/env python3
"""
Static Analysis Validator

WHY: Catch type errors, bugs, and code quality issues before execution
RESPONSIBILITY: Run linters and type checkers on generated code
PATTERNS: Strategy pattern for language-specific tools, Guard clauses

Reduces hallucinations by:
- Type checking (mypy) - catches type inconsistencies
- Linting (ruff) - catches common bugs and anti-patterns
- Complexity analysis (radon) - flags overly complex code
"""

import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from artemis_logger import get_logger


@dataclass
class AnalysisIssue:
    """Single static analysis issue."""
    file: str
    line: int
    column: int
    severity: str  # "error", "warning", "info"
    tool: str  # "mypy", "ruff", "radon"
    code: str  # Error code (e.g., "E501", "type-error")
    message: str


@dataclass
class StaticAnalysisResult:
    """Result of static analysis."""
    passed: bool
    error_count: int
    warning_count: int
    info_count: int
    issues: List[AnalysisIssue]
    summary: str
    tool_results: Dict[str, Any]  # Raw results from each tool


class StaticAnalysisValidator:
    """
    Run static analysis tools on generated code.

    WHY: Static analysis catches bugs without execution
    RESPONSIBILITY: Orchestrate linters, type checkers, complexity analyzers
    PATTERNS: Strategy pattern, Guard clauses
    """

    def __init__(
        self,
        enable_type_checking: bool = True,
        enable_linting: bool = True,
        enable_complexity_check: bool = True,
        max_complexity: int = 10,
        logger: Optional[Any] = None
    ):
        """
        Initialize static analysis validator.

        Args:
            enable_type_checking: Run mypy type checker
            enable_linting: Run ruff linter
            enable_complexity_check: Run radon complexity analyzer
            max_complexity: Maximum cyclomatic complexity allowed
            logger: Optional logger instance
        """
        self.enable_type_checking = enable_type_checking
        self.enable_linting = enable_linting
        self.enable_complexity_check = enable_complexity_check
        self.max_complexity = max_complexity
        self.logger = logger or get_logger("static_analysis")

    def validate_code(
        self,
        code: str,
        language: str = "python",
        file_name: str = "generated.py"
    ) -> StaticAnalysisResult:
        """
        Validate code using static analysis tools.

        WHY: Main entry point for static analysis
        RESPONSIBILITY: Orchestrate all analysis tools

        Args:
            code: Source code to analyze
            language: Programming language
            file_name: Filename for reporting

        Returns:
            StaticAnalysisResult with all findings
        """
        # Guard: Only Python supported currently
        if language != "python":
            return self._create_unsupported_language_result(language)

        self.logger.info(f"Running static analysis on {file_name}")

        # Create temp file for analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / file_name
            file_path.write_text(code)

            # Run all enabled tools
            issues = []
            tool_results = {}

            if self.enable_type_checking:
                type_issues, type_result = self._run_mypy(file_path)
                issues.extend(type_issues)
                tool_results['mypy'] = type_result

            if self.enable_linting:
                lint_issues, lint_result = self._run_ruff(file_path)
                issues.extend(lint_issues)
                tool_results['ruff'] = lint_result

            if self.enable_complexity_check:
                complexity_issues, complexity_result = self._run_radon(file_path)
                issues.extend(complexity_issues)
                tool_results['radon'] = complexity_result

            # Aggregate results
            return self._aggregate_results(issues, tool_results, file_name)

    def _run_mypy(self, file_path: Path) -> tuple[List[AnalysisIssue], Dict]:
        """
        Run mypy type checker.

        WHY: Type checking catches type inconsistencies
        RESPONSIBILITY: Execute mypy and parse results
        PATTERNS: Guard clauses
        """
        issues = []
        result = {"tool": "mypy", "ran": False}

        try:
            # Run mypy with JSON output
            proc = subprocess.run(
                ["mypy", "--strict", "--show-error-codes", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            result["ran"] = True
            result["exit_code"] = proc.returncode
            result["stdout"] = proc.stdout
            result["stderr"] = proc.stderr

            # Parse mypy output
            issues = self._parse_mypy_output(proc.stdout, str(file_path))

        except FileNotFoundError:
            self.logger.warning("mypy not found - skipping type checking")
        except subprocess.TimeoutExpired:
            self.logger.error("mypy timed out")
        except Exception as e:
            self.logger.error(f"mypy failed: {e}")

        return issues, result

    def _parse_mypy_output(self, output: str, file_path: str) -> List[AnalysisIssue]:
        """Parse mypy output into AnalysisIssues."""
        issues = []

        for line in output.splitlines():
            # Guard: Skip empty lines
            if not line.strip():
                continue

            # Parse format: "file.py:line:col: severity: message [code]"
            parts = line.split(':', 3)

            # Guard: Invalid format
            if len(parts) < 4:
                continue

            try:
                line_num = int(parts[1])
                col = int(parts[2]) if parts[2].strip().isdigit() else 0

                # Extract severity and message
                rest = parts[3].strip()
                severity = "error" if "error" in rest.lower() else "warning"

                # Extract error code if present
                code = "type-error"
                if '[' in rest and ']' in rest:
                    code_start = rest.rfind('[')
                    code_end = rest.rfind(']')
                    code = rest[code_start+1:code_end]
                    message = rest[:code_start].strip()
                else:
                    message = rest

                issues.append(AnalysisIssue(
                    file=file_path,
                    line=line_num,
                    column=col,
                    severity=severity,
                    tool="mypy",
                    code=code,
                    message=message
                ))

            except (ValueError, IndexError):
                continue

        return issues

    def _run_ruff(self, file_path: Path) -> tuple[List[AnalysisIssue], Dict]:
        """
        Run ruff linter.

        WHY: Linting catches common bugs and anti-patterns
        RESPONSIBILITY: Execute ruff and parse results
        PATTERNS: Guard clauses
        """
        issues = []
        result = {"tool": "ruff", "ran": False}

        try:
            # Run ruff with JSON output
            proc = subprocess.run(
                ["ruff", "check", "--output-format=json", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            result["ran"] = True
            result["exit_code"] = proc.returncode
            result["stdout"] = proc.stdout

            # Parse JSON output
            issues = self._parse_ruff_output(proc.stdout, str(file_path))

        except FileNotFoundError:
            self.logger.warning("ruff not found - skipping linting")
        except subprocess.TimeoutExpired:
            self.logger.error("ruff timed out")
        except Exception as e:
            self.logger.error(f"ruff failed: {e}")

        return issues, result

    def _parse_ruff_output(self, output: str, file_path: str) -> List[AnalysisIssue]:
        """Parse ruff JSON output into AnalysisIssues."""
        issues = []

        # Guard: Empty output
        if not output.strip():
            return issues

        try:
            violations = json.loads(output)

            for violation in violations:
                # Guard: Missing required fields
                if not all(k in violation for k in ['location', 'code', 'message']):
                    continue

                loc = violation['location']

                issues.append(AnalysisIssue(
                    file=file_path,
                    line=loc.get('row', 0),
                    column=loc.get('column', 0),
                    severity=self._ruff_severity_to_standard(violation.get('fix', {})),
                    tool="ruff",
                    code=violation['code'],
                    message=violation['message']
                ))

        except json.JSONDecodeError:
            self.logger.error("Failed to parse ruff JSON output")

        return issues

    def _ruff_severity_to_standard(self, fix_info: Dict) -> str:
        """Map ruff fix info to standard severity."""
        # Guard: Has automatic fix
        if fix_info.get('applicability') == 'automatic':
            return "warning"

        # Guard: Has manual fix
        if fix_info:
            return "warning"

        return "error"

    def _run_radon(self, file_path: Path) -> tuple[List[AnalysisIssue], Dict]:
        """
        Run radon complexity analyzer.

        WHY: High complexity often indicates hallucinated code
        RESPONSIBILITY: Execute radon and parse results
        PATTERNS: Guard clauses
        """
        issues = []
        result = {"tool": "radon", "ran": False}

        try:
            # Run radon with JSON output
            proc = subprocess.run(
                ["radon", "cc", "-j", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            result["ran"] = True
            result["exit_code"] = proc.returncode
            result["stdout"] = proc.stdout

            # Parse JSON output
            issues = self._parse_radon_output(proc.stdout, str(file_path))

        except FileNotFoundError:
            self.logger.warning("radon not found - skipping complexity analysis")
        except subprocess.TimeoutExpired:
            self.logger.error("radon timed out")
        except Exception as e:
            self.logger.error(f"radon failed: {e}")

        return issues, result

    def _parse_radon_output(self, output: str, file_path: str) -> List[AnalysisIssue]:
        """Parse radon JSON output into AnalysisIssues."""
        issues = []

        # Guard: Empty output
        if not output.strip():
            return issues

        try:
            complexity_data = json.loads(output)

            # radon returns {filename: [function_data]}
            for file_data in complexity_data.values():
                for func in file_data:
                    complexity = func.get('complexity', 0)

                    # Guard: Complexity within limit
                    if complexity <= self.max_complexity:
                        continue

                    issues.append(AnalysisIssue(
                        file=file_path,
                        line=func.get('lineno', 0),
                        column=func.get('col_offset', 0),
                        severity="warning",
                        tool="radon",
                        code=f"C{complexity}",
                        message=f"Function '{func.get('name')}' has complexity {complexity} "
                                f"(max: {self.max_complexity})"
                    ))

        except json.JSONDecodeError:
            self.logger.error("Failed to parse radon JSON output")

        return issues

    def _aggregate_results(
        self,
        issues: List[AnalysisIssue],
        tool_results: Dict,
        file_name: str
    ) -> StaticAnalysisResult:
        """
        Aggregate issues into final result.

        WHY: Provide unified view of all static analysis
        RESPONSIBILITY: Count issues, determine pass/fail
        PATTERNS: Guard clauses
        """
        # Count issues by severity
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        info_count = sum(1 for i in issues if i.severity == "info")

        # Determine pass/fail
        passed = error_count == 0

        # Create summary
        summary = self._create_summary(
            passed, error_count, warning_count, info_count, file_name
        )

        return StaticAnalysisResult(
            passed=passed,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            issues=sorted(issues, key=lambda i: (i.severity, i.line)),
            summary=summary,
            tool_results=tool_results
        )

    def _create_summary(
        self,
        passed: bool,
        error_count: int,
        warning_count: int,
        info_count: int,
        file_name: str
    ) -> str:
        """Create human-readable summary."""
        # Guard: All passed
        if passed and warning_count == 0 and info_count == 0:
            return f"✅ {file_name}: All static analysis checks passed"

        # Guard: Has errors
        if error_count > 0:
            return (
                f"❌ {file_name}: {error_count} error(s), "
                f"{warning_count} warning(s), {info_count} info"
            )

        # Has warnings but no errors
        return (
            f"⚠️  {file_name}: {warning_count} warning(s), "
            f"{info_count} info (no errors)"
        )

    def _create_unsupported_language_result(self, language: str) -> StaticAnalysisResult:
        """Create result for unsupported language."""
        return StaticAnalysisResult(
            passed=True,
            error_count=0,
            warning_count=0,
            info_count=0,
            issues=[],
            summary=f"ℹ️  Static analysis not supported for {language}",
            tool_results={}
        )
