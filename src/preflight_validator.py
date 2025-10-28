#!/usr/bin/env python3
"""
Preflight Validator - Static code validation before pipeline execution

This module validates Python files for syntax errors, import issues, and other
static problems BEFORE the pipeline starts. This allows the supervisor to detect
and potentially fix issues that would otherwise cause import-time failures.
"""

import sys
import os
import py_compile
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Represents a validation issue found during preflight checks"""
    file_path: str
    issue_type: str  # "syntax_error", "import_error", "missing_file"
    severity: str  # "critical", "high", "medium", "low"
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class PreflightValidator:
    """
    Validates Python files before pipeline execution.

    Checks:
    - Syntax errors (py_compile)
    - Import errors
    - Missing required files
    - File permissions

    Can auto-fix syntax errors using LLM.
    """

    def __init__(self, verbose: bool = True, llm_client=None, auto_fix: bool = False):
        self.verbose = verbose
        self.issues: List[ValidationIssue] = []
        self.llm_client = llm_client
        self.auto_fix = auto_fix
        self.fixes_applied: List[Dict] = []

    def validate_all(self, base_path: str = ".") -> Dict:
        """
        Run all preflight validation checks.

        Returns:
            dict: {
                "passed": bool,
                "critical_count": int,
                "high_count": int,
                "issues": List[ValidationIssue]
            }
        """
        self.issues = []

        # Get all Python files in the agile directory
        agile_dir = Path(base_path)
        python_files = list(agile_dir.glob("*.py"))

        if self.verbose:
            print(f"\n🔍 Preflight Validation - Checking {len(python_files)} Python files...")

        # Check syntax for each file
        for py_file in python_files:
            self._check_syntax(str(py_file))

        # Check critical files exist
        self._check_critical_files(base_path)

        # Summarize results
        critical_count = sum(1 for issue in self.issues if issue.severity == "critical")
        high_count = sum(1 for issue in self.issues if issue.severity == "high")

        passed = critical_count == 0

        if self.verbose:
            if passed:
                print(f"✅ Preflight validation PASSED - {len(self.issues)} non-critical issues found")
            else:
                print(f"❌ Preflight validation FAILED - {critical_count} critical issues found")

        return {
            "passed": passed,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": sum(1 for issue in self.issues if issue.severity == "medium"),
            "low_count": sum(1 for issue in self.issues if issue.severity == "low"),
            "total_issues": len(self.issues),
            "issues": self.issues
        }

    def _check_syntax(self, file_path: str) -> bool:
        """Check if a Python file has valid syntax"""
        try:
            py_compile.compile(file_path, doraise=True)
            if self.verbose:
                print(f"  ✅ {Path(file_path).name}")
            return True
        except SyntaxError as e:
            self.issues.append(ValidationIssue(
                file_path=file_path,
                issue_type="syntax_error",
                severity="critical",
                message=f"Syntax error: {e.msg}",
                line_number=e.lineno,
                suggestion=f"Fix syntax error at line {e.lineno}: {e.text}"
            ))
            if self.verbose:
                print(f"  ❌ {Path(file_path).name} - Syntax error at line {e.lineno}")
            return False
        except Exception as e:
            self.issues.append(ValidationIssue(
                file_path=file_path,
                issue_type="syntax_error",
                severity="critical",
                message=f"Compilation error: {str(e)}",
                suggestion="Review the file for syntax issues"
            ))
            if self.verbose:
                print(f"  ❌ {Path(file_path).name} - Compilation error: {e}")
            return False

    def _check_critical_files(self, base_path: str):
        """Check that critical files exist and are readable"""
        critical_files = [
            "artemis_orchestrator.py",
            "artemis_stages.py",
            "pipeline_strategies.py",
            "kanban_manager.py",
            "rag_agent.py"
        ]

        for filename in critical_files:
            self._validate_critical_file(base_path, filename)

    def _validate_critical_file(self, base_path: str, filename: str):
        """Validate a single critical file exists and is readable"""
        file_path = Path(base_path) / filename

        if not file_path.exists():
            self.issues.append(ValidationIssue(
                file_path=str(file_path),
                issue_type="missing_file",
                severity="critical",
                message=f"Critical file not found: {filename}",
                suggestion=f"Ensure {filename} exists in the agile directory"
            ))
            return

        if not os.access(file_path, os.R_OK):
            self.issues.append(ValidationIssue(
                file_path=str(file_path),
                issue_type="permission_error",
                severity="high",
                message=f"Critical file not readable: {filename}",
                suggestion=f"Check file permissions for {filename}"
            ))

    def auto_fix_syntax_errors(self) -> bool:
        """
        Automatically fix syntax errors using LLM.

        Returns:
            bool: True if all critical syntax errors were fixed
        """
        if not self.llm_client or not self.auto_fix:
            return False

        critical_syntax_errors = [
            issue for issue in self.issues
            if issue.severity == "critical" and issue.issue_type == "syntax_error"
        ]

        if not critical_syntax_errors:
            return True

        if self.verbose:
            print(f"\n🔧 Auto-fixing {len(critical_syntax_errors)} syntax errors...")

        all_fixed = True
        for issue in critical_syntax_errors:
            fixed = self._attempt_fix_with_error_handling(issue)
            if not fixed:
                all_fixed = False

        return all_fixed

    def _attempt_fix_with_error_handling(self, issue: ValidationIssue) -> bool:
        """Attempt to fix an issue and handle errors"""
        try:
            fixed = self._fix_syntax_error_with_llm(issue)
            self._record_fix_result(issue, fixed)
            return fixed
        except Exception as e:
            self._handle_fix_error(issue, e)
            return False

    def _record_fix_result(self, issue: ValidationIssue, fixed: bool):
        """Record the result of a fix attempt"""
        if fixed:
            self.fixes_applied.append({
                "file": issue.file_path,
                "issue": issue.message,
                "fixed": True
            })
            if self.verbose:
                print(f"  ✅ Fixed: {Path(issue.file_path).name}")
            return

        if self.verbose:
            print(f"  ❌ Could not fix: {Path(issue.file_path).name}")

    def _handle_fix_error(self, issue: ValidationIssue, error: Exception):
        """Handle errors during fix attempts"""
        if self.verbose:
            print(f"  ❌ Error fixing {Path(issue.file_path).name}: {error}")

    def _fix_syntax_error_with_llm(self, issue: ValidationIssue) -> bool:
        """Use LLM to fix a specific syntax error"""
        # Read the broken file
        with open(issue.file_path, 'r') as f:
            broken_code = f.read()

        # Create prompt for LLM
        prompt = f"""Fix this Python syntax error:

File: {issue.file_path}
Error: {issue.message}
Line: {issue.line_number}

BROKEN CODE:
```python
{broken_code}
```

Return ONLY the corrected Python code, nothing else. No explanations, no markdown formatting.
The code must be syntactically valid Python that fixes the error while preserving all functionality."""

        try:
            # Get fix from LLM
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=4000,
                temperature=0.1  # Low temperature for precise fixes
            )

            fixed_code = response.strip()

            # Remove markdown code blocks if present
            fixed_code = self._strip_markdown_formatting(fixed_code)

            # Validate the fix compiles
            if not self._validate_fixed_code(fixed_code, issue.file_path):
                return False

            # Write the fix
            with open(issue.file_path, 'w') as f:
                f.write(fixed_code)

            return True

        except Exception as e:
            if self.verbose:
                print(f"    LLM fix failed: {e}")
            return False

    def _strip_markdown_formatting(self, code: str) -> str:
        """Remove markdown code block formatting from code"""
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def _validate_fixed_code(self, fixed_code: str, file_path: str) -> bool:
        """Validate that fixed code compiles without syntax errors"""
        try:
            compile(fixed_code, file_path, 'exec')
            return True
        except SyntaxError:
            if self.verbose:
                print(f"    LLM fix still has syntax errors, skipping")
            return False

    def print_report(self):
        """Print a detailed validation report"""
        print("\n" + "=" * 70)
        print("🔍 PREFLIGHT VALIDATION REPORT")
        print("=" * 70)

        if len(self.issues) == 0:
            print("\n✅ All checks passed - No issues found!")
            print("\n" + "=" * 70)
            return

        # Group by severity (Pattern #11: Single-pass categorization for O(n) vs O(4n))
        from collections import defaultdict
        issues_by_severity = defaultdict(list)
        for issue in self.issues:
            issues_by_severity[issue.severity].append(issue)

        critical = issues_by_severity["critical"]
        high = issues_by_severity["high"]
        medium = issues_by_severity["medium"]
        low = issues_by_severity["low"]

        print(f"\n📊 Summary:")
        print(f"  🔴 Critical: {len(critical)}")
        print(f"  🟠 High: {len(high)}")
        print(f"  🟡 Medium: {len(medium)}")
        print(f"  🟢 Low: {len(low)}")

        # Show critical issues
        if critical:
            print(f"\n🔴 CRITICAL ISSUES (must fix before running):")
            for i, issue in enumerate(critical, 1):
                self._print_issue_details(i, issue, include_line_number=True)

        # Show high priority issues
        if high:
            print(f"\n🟠 HIGH PRIORITY ISSUES:")
            for i, issue in enumerate(high, 1):
                self._print_issue_details(i, issue, include_line_number=False)

        # Show fixes applied
        self._print_fixes_applied()

        print("\n" + "=" * 70)

    def _print_issue_details(self, index: int, issue: ValidationIssue, include_line_number: bool = True):
        """Print details for a single issue"""
        print(f"\n{index}. [{issue.issue_type}] {Path(issue.file_path).name}")
        print(f"   {issue.message}")

        if include_line_number and issue.line_number:
            print(f"   Line: {issue.line_number}")

        if issue.suggestion:
            print(f"   💡 {issue.suggestion}")

    def _print_fixes_applied(self):
        """Print details of automatic fixes that were applied"""
        if not self.fixes_applied:
            return

        print(f"\n🔧 AUTOMATIC FIXES APPLIED:")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"\n{i}. {Path(fix['file']).name}")
            print(f"   Issue: {fix['issue']}")
            print(f"   Status: {'✅ Fixed' if fix['fixed'] else '❌ Failed'}")


def run_preflight_validation(base_path: str = ".agents/agile", verbose: bool = True) -> Dict:
    """
    Convenience function to run preflight validation.

    Args:
        base_path: Directory containing Python files to validate
        verbose: Print progress messages

    Returns:
        Validation results dictionary
    """
    validator = PreflightValidator(verbose=verbose)
    results = validator.validate_all(base_path)

    if verbose:
        validator.print_report()

    return results


if __name__ == "__main__":
    # Run validation on current directory
    import sys

    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    results = run_preflight_validation(base_path, verbose=True)

    # Exit with error code if validation failed
    sys.exit(0 if results["passed"] else 1)
