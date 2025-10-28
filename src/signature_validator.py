#!/usr/bin/env python3
"""
Function Signature Validator for Artemis

WHY: Detects parameter signature mismatches in method/function calls.
Complements code_standards_scanner.py by checking for incorrect argument counts,
missing required parameters, and extra unexpected parameters.

USAGE:
    from signature_validator import SignatureValidator

    validator = SignatureValidator()
    result = validator.validate_file("src/my_module.py")

    for issue in result.issues:
        print(f"{issue['file']}:{issue['line']} - {issue['message']}")
"""

import ast
import inspect
import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class SignatureIssue:
    """Represents a function signature mismatch"""
    file_path: str
    line_number: int
    function_name: str
    issue_type: str  # 'too_many_args', 'too_few_args', 'unknown_kwarg', 'missing_required'
    message: str
    severity: str = "warning"


class SignatureValidator:
    """
    Validates function/method call signatures

    WHY: Catches common errors where functions are called with
    incorrect numbers of arguments or invalid keyword arguments.

    LIMITATION: This is a best-effort static analysis tool.
    It cannot detect all signature mismatches (e.g., dynamic calls,
    * args/**kwargs) but catches common mistakes.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the signature validator

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.issues: List[SignatureIssue] = []
        self.function_signatures: Dict[str, inspect.Signature] = {}

    def validate_file(self, file_path: str) -> List[SignatureIssue]:
        """
        Validate function call signatures in a Python file

        WHY: Provides static analysis of function calls to catch
        signature mismatches before runtime.

        Args:
            file_path: Path to Python file to validate

        Returns:
            List of SignatureIssue objects
        """
        self.issues = []

        if not Path(file_path).exists():
            return self.issues

        try:
            with open(file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)

            # First pass: collect function definitions
            self._collect_function_signatures(tree, file_path)

            # Second pass: validate function calls
            self._validate_calls(tree, file_path)

        except SyntaxError as e:
            if self.verbose:
                print(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            if self.verbose:
                print(f"Error validating {file_path}: {e}")

        return self.issues

    def validate_directory(
        self,
        dir_path: str,
        exclude_dirs: Optional[Set[str]] = None
    ) -> List[SignatureIssue]:
        """
        Validate all Python files in a directory

        Args:
            dir_path: Directory to scan
            exclude_dirs: Directories to skip

        Returns:
            List of all SignatureIssue objects found
        """
        if exclude_dirs is None:
            exclude_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.artemis_data'}

        all_issues = []

        for py_file in Path(dir_path).rglob('*.py'):
            # Skip excluded directories
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue

            issues = self.validate_file(str(py_file))
            all_issues.extend(issues)

        return all_issues

    def _collect_function_signatures(self, tree: ast.AST, file_path: str):
        """
        Collect function signatures from AST

        WHY: Build a map of function names to their parameter lists
        for validation in second pass.
        """
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name

                # Build parameter info
                params = {
                    'args': [],
                    'defaults': [],
                    'kwonly': [],
                    'kwdefaults': []
                }

                # Regular args
                for arg in node.args.args:
                    params['args'].append(arg.arg)

                # Defaults (aligned to the right of args list)
                defaults = node.args.defaults
                if defaults:
                    params['defaults'] = defaults

                # Keyword-only args
                for arg in node.args.kwonlyargs:
                    params['kwonly'].append(arg.arg)

                # Keyword-only defaults
                params['kwdefaults'] = node.args.kw_defaults

                # Store with simple key (just function name)
                # Note: This doesn't handle class methods perfectly,
                # but catches most issues
                self.function_signatures[func_name] = params

    def _validate_calls(self, tree: ast.AST, file_path: str):
        """
        Validate function calls against collected signatures

        WHY: Check each Call node to see if it matches the signature
        of the function being called.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                self._validate_single_call(node, file_path)

    def _validate_single_call(self, call_node: ast.Call, file_path: str):
        """Validate a single function call"""
        # Get function name
        func_name = self._get_function_name(call_node.func)

        if not func_name:
            return  # Can't determine function name (e.g., lambda, complex expression)

        # Check if we have signature info
        if func_name not in self.function_signatures:
            return  # Function defined elsewhere or built-in

        signature = self.function_signatures[func_name]

        # Count positional arguments
        num_positional = len(call_node.args)

        # Count keyword arguments
        kwarg_names = {kw.arg for kw in call_node.keywords if kw.arg}  # Exclude **kwargs

        # Get expected params
        expected_args = signature['args']
        num_defaults = len(signature['defaults'])
        num_required = len(expected_args) - num_defaults

        kwonly_args = set(signature['kwonly'])
        kwonly_defaults = signature['kwdefaults']

        # Check for too many positional arguments
        if num_positional > len(expected_args):
            self.issues.append(SignatureIssue(
                file_path=file_path,
                line_number=call_node.lineno,
                function_name=func_name,
                issue_type='too_many_args',
                message=f"Too many arguments to {func_name}(): expected {len(expected_args)}, got {num_positional}",
                severity='warning'
            ))

        # Check for too few arguments (not covered by kwargs)
        provided_args = set(expected_args[:num_positional]) | kwarg_names
        required_args = set(expected_args[:num_required])

        missing_args = required_args - provided_args

        if missing_args:
            self.issues.append(SignatureIssue(
                file_path=file_path,
                line_number=call_node.lineno,
                function_name=func_name,
                issue_type='missing_required',
                message=f"Missing required arguments to {func_name}(): {', '.join(sorted(missing_args))}",
                severity='critical'
            ))

        # Check for unknown keyword arguments
        all_valid_kwargs = set(expected_args) | kwonly_args
        unknown_kwargs = kwarg_names - all_valid_kwargs

        if unknown_kwargs:
            self.issues.append(SignatureIssue(
                file_path=file_path,
                line_number=call_node.lineno,
                function_name=func_name,
                issue_type='unknown_kwarg',
                message=f"Unknown keyword argument(s) to {func_name}(): {', '.join(sorted(unknown_kwargs))}",
                severity='critical'
            ))

    def _get_function_name(self, func_node: ast.AST) -> Optional[str]:
        """Extract function name from call node"""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            return func_node.attr
        else:
            return None  # Complex expression, can't determine


def _get_severity_icon(severity: str) -> str:
    """
    Get icon for severity level.

    WHY: DRY - extract severity mapping to avoid inline dictionary creation.

    Args:
        severity: Severity level ('critical', 'warning', 'info')

    Returns:
        Emoji icon for severity
    """
    severity_icons = {
        'critical': '🚨',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    return severity_icons.get(severity, 'ℹ️')


def _print_issue(issue: SignatureIssue):
    """
    Print single signature issue.

    WHY: Extract helper method to reduce nesting and improve readability.

    Args:
        issue: SignatureIssue to print
    """
    severity_icon = _get_severity_icon(issue.severity)
    print(f"{severity_icon} {issue.file_path}:{issue.line_number}")
    print(f"   {issue.message}\n")


def _print_issues(issues: List[SignatureIssue]):
    """
    Print all signature issues and exit with appropriate code.

    WHY: Extract helper method to avoid nested if statements.

    Args:
        issues: List of SignatureIssue objects
    """
    print(f"\n🔍 Found {len(issues)} signature issues:\n")

    for issue in issues:
        _print_issue(issue)

    # Exit with error code if critical issues found
    critical_count = sum(1 for i in issues if i.severity == 'critical')
    sys.exit(1 if critical_count > 0 else 0)


def _validate_target(validator: SignatureValidator, target: str) -> List[SignatureIssue]:
    """
    Validate file or directory target.

    WHY: Extract helper method to reduce nesting (early return pattern).

    Args:
        validator: SignatureValidator instance
        target: File or directory path to validate

    Returns:
        List of SignatureIssue objects found
    """
    if Path(target).is_file():
        return validator.validate_file(target)
    return validator.validate_directory(target)


def _run_validation_cli():
    """
    Run signature validation CLI.

    WHY: Extract main logic to helper method with early returns (avoid nesting).
    PATTERNS: Guard clauses with early returns for cleaner control flow.
    """
    # Guard clause: Check arguments
    if len(sys.argv) <= 1:
        print("Usage: python3 signature_validator.py <file_or_directory>")
        sys.exit(1)

    # Validate target
    validator = SignatureValidator(verbose=True)
    target = sys.argv[1]
    issues = _validate_target(validator, target)

    # Guard clause: No issues found
    if not issues:
        print("✅ No signature issues found!")
        sys.exit(0)

    # Print issues and exit
    _print_issues(issues)


# Example usage
if __name__ == "__main__":
    _run_validation_cli()
