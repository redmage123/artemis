#!/usr/bin/env python3
"""
WHY: Implement concrete validators for each validation stage.

RESPONSIBILITY: Provide stage-specific validation logic for imports, signatures,
docstrings, body, tests, and full code validation.

PATTERNS:
- Strategy pattern for different validation strategies
- Guard clauses for early returns
- Single Responsibility - each validator focuses on one stage
"""

import ast
import re
from typing import Dict, List, Tuple, Optional

from .validator_base import BaseValidator, ValidatorHelper
from .models import ValidationContext


class ImportsValidator(BaseValidator):
    """
    WHY: Validate import statements for correctness and security.

    RESPONSIBILITY: Check imports are parseable, non-dangerous, and complete.
    """

    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """Validate import statements."""
        checks = {}
        feedback = []

        lines, code_lines = ValidatorHelper.parse_code_lines(code)

        # Check 1: Has imports (if code is non-trivial)
        import_checks, import_feedback = self._check_has_imports(code, code_lines)
        checks.update(import_checks)
        feedback.extend(import_feedback)

        # Check 2: Try to parse imports
        try:
            tree = ast.parse(code)
            import_nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
            checks['imports_parseable'] = True

            # Check 3: No star imports
            star_imports = [
                n for n in import_nodes
                if isinstance(n, ast.ImportFrom) and any(alias.name == '*' for alias in n.names)
            ]
            checks['no_star_imports'] = len(star_imports) == 0

            if star_imports:
                feedback.append("Avoid star imports (from X import *) - import specific names")

        except SyntaxError as e:
            checks['imports_parseable'] = False
            feedback.append(f"Import syntax error: {e.msg}")

        # Check 4: No dangerous imports
        dangerous_checks, dangerous_feedback = self._check_dangerous_imports(code)
        checks.update(dangerous_checks)
        feedback.extend(dangerous_feedback)

        # Check 5: Required imports from context
        if context and context.required_imports:
            required_checks, required_feedback = self._check_required_imports(
                code, context.required_imports
            )
            checks.update(required_checks)
            feedback.extend(required_feedback)

        severity = ValidatorHelper.determine_severity(checks, ['imports_parseable'])

        return checks, feedback, severity

    def _check_dangerous_imports(self, code: str) -> Tuple[Dict[str, bool], List[str]]:
        """Check for dangerous imports."""
        checks = {}
        feedback = []

        bad_imports = [
            'from os import system',
            'import pickle',
            '__import__'
        ]

        for bad in bad_imports:
            if bad in code:
                safe_key = bad.replace(' ', '_').replace('(', '').replace(')', '')
                checks[f'no_dangerous_import_{safe_key}'] = False
                feedback.append(f"Dangerous import detected: {bad}")

        return checks, feedback


class SignatureValidator(BaseValidator):
    """
    WHY: Validate function and class signatures for type hints and documentation.

    RESPONSIBILITY: Check signatures have proper type hints and docstrings.
    """

    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """Validate function/class signatures."""
        checks = {}
        feedback = []

        try:
            tree = ast.parse(code)

            # Validate functions
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            for func in functions:
                func_checks, func_feedback = self._check_function_signature(func)
                checks.update(func_checks)
                feedback.extend(func_feedback)

            # Validate classes
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            for cls in classes:
                cls_checks, cls_feedback = self._check_class_signature(cls)
                checks.update(cls_checks)
                feedback.extend(cls_feedback)

            checks['parseable'] = True

        except SyntaxError as e:
            checks['parseable'] = False
            feedback.append(f"Signature syntax error: {e.msg}")

        severity = ValidatorHelper.determine_severity(checks, ['parseable'])

        return checks, feedback, severity

    def _check_function_signature(self, func: ast.FunctionDef) -> Tuple[Dict[str, bool], List[str]]:
        """Check a single function signature."""
        checks = {}
        feedback = []

        # Check 1: Has docstring
        has_docstring = ast.get_docstring(func) is not None
        checks[f'{func.name}_has_docstring'] = has_docstring

        if not has_docstring:
            feedback.append(f"Function '{func.name}' missing docstring")

        # Check 2: Has return type hint
        has_return_hint = func.returns is not None
        checks[f'{func.name}_has_return_hint'] = has_return_hint

        if not has_return_hint and func.name != '__init__':
            feedback.append(f"Function '{func.name}' missing return type hint")

        # Check 3: Parameters have type hints
        non_self_args = [arg for arg in func.args.args if arg.arg not in ['self', 'cls']]

        # Guard: No parameters to check
        if not non_self_args:
            return checks, feedback

        args_with_hints = [arg for arg in func.args.args if arg.annotation is not None]
        param_hint_ratio = len(args_with_hints) / len(func.args.args)
        checks[f'{func.name}_params_typed'] = param_hint_ratio > 0.5

        if param_hint_ratio < 0.5:
            feedback.append(f"Function '{func.name}' parameters need type hints")

        return checks, feedback

    def _check_class_signature(self, cls: ast.ClassDef) -> Tuple[Dict[str, bool], List[str]]:
        """Check a single class signature."""
        checks = {}
        feedback = []

        has_docstring = ast.get_docstring(cls) is not None
        checks[f'{cls.name}_has_docstring'] = has_docstring

        if not has_docstring:
            feedback.append(f"Class '{cls.name}' missing docstring")

        return checks, feedback


class DocstringValidator(BaseValidator):
    """
    WHY: Validate docstring quality and completeness.

    RESPONSIBILITY: Check docstrings exist and contain required sections.
    """

    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """Validate docstrings."""
        checks = {}
        feedback = []

        try:
            tree = ast.parse(code)

            # Check module docstring
            module_docstring = ast.get_docstring(tree)
            checks['has_module_docstring'] = module_docstring is not None

            if not module_docstring:
                feedback.append("Missing module-level docstring")

            # Check function docstrings
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            for func in functions:
                # Skip private methods (but not dunder methods)
                if func.name.startswith('_') and not func.name.startswith('__'):
                    continue

                doc_checks, doc_feedback = self._check_function_docstring(func)
                checks.update(doc_checks)
                feedback.extend(doc_feedback)

        except SyntaxError as e:
            checks['parseable'] = False
            feedback.append(f"Syntax error when checking docstrings: {e.msg}")

        severity = "low"  # Docstrings are important but not critical

        return checks, feedback, severity

    def _check_function_docstring(self, func: ast.FunctionDef) -> Tuple[Dict[str, bool], List[str]]:
        """Check a single function docstring."""
        checks = {}
        feedback = []

        docstring = ast.get_docstring(func)
        checks[f'{func.name}_docstring'] = docstring is not None

        # Guard: No docstring
        if not docstring:
            feedback.append(f"Function '{func.name}' missing docstring")
            return checks, feedback

        # Check docstring quality
        has_args_section = 'Args:' in docstring or 'Parameters:' in docstring
        has_returns_section = 'Returns:' in docstring or 'Return:' in docstring

        if func.args.args and not has_args_section:
            checks[f'{func.name}_docstring_has_args'] = False
            feedback.append(f"Docstring for '{func.name}' missing Args section")

        if func.returns and not has_returns_section and func.name != '__init__':
            checks[f'{func.name}_docstring_has_returns'] = False
            feedback.append(f"Docstring for '{func.name}' missing Returns section")

        return checks, feedback


class BodyValidator(BaseValidator):
    """
    WHY: Validate function/class body implementation for completeness.

    RESPONSIBILITY: Check body has no placeholders, compiles, and follows best practices.
    """

    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """Validate function/class body."""
        checks = {}
        feedback = []

        # Check 1: No placeholders (CRITICAL)
        placeholder_checks, placeholder_feedback = self._check_placeholders(code)
        checks.update(placeholder_checks)
        feedback.extend(placeholder_feedback)

        # Check 2: No obvious errors
        error_checks, error_feedback = self._check_error_patterns(code)
        checks.update(error_checks)
        feedback.extend(error_feedback)

        # Check 3: Syntax and compilation
        syntax_checks, syntax_feedback = self._check_syntax(code)
        checks.update(syntax_checks)
        feedback.extend(syntax_feedback)

        # Check 4: Expected methods (if context provided)
        if context and context.expected_methods:
            method_checks, method_feedback = self._check_expected_methods(
                code, context.expected_methods
            )
            checks.update(method_checks)
            feedback.extend(method_feedback)

        severity = ValidatorHelper.determine_severity(checks, ['syntax_valid', 'compiles'])

        return checks, feedback, severity

    def _check_placeholders(self, code: str) -> Tuple[Dict[str, bool], List[str]]:
        """Check for placeholder code."""
        checks = {}
        feedback = []

        placeholders = [
            'TODO',
            'FIXME',
            'XXX',
            '...',
            'pass  # implementation',
            'raise NotImplementedError'
        ]

        for placeholder in placeholders:
            if placeholder in code:
                safe_key = placeholder.lower().replace(' ', '_').replace('#', '').strip()
                checks[f'no_{safe_key}'] = False
                feedback.append(f"Found placeholder: '{placeholder}' - code must be complete")

        return checks, feedback

    def _check_error_patterns(self, code: str) -> Tuple[Dict[str, bool], List[str]]:
        """Check for common framework errors."""
        checks = {}
        feedback = []

        error_patterns = [
            (r'\.save\(\)', "SQLAlchemy uses db.session.add() and commit(), not .save()"),
            (r'User\.create\(', "SQLAlchemy uses User() constructor + db.session.add(), not .create()"),
            (r'\.find\(\)', "SQLAlchemy uses .query().filter(), not .find()"),
        ]

        for pattern, message in error_patterns:
            if re.search(pattern, code):
                safe_key = pattern[:20].replace('\\', '').replace('.', '').replace('(', '')
                checks[f'no_error_{safe_key}'] = False
                feedback.append(message)

        return checks, feedback

    def _check_syntax(self, code: str) -> Tuple[Dict[str, bool], List[str]]:
        """Check syntax and compilation."""
        checks = {}
        feedback = []

        try:
            tree = ast.parse(code)
            compile(code, '<string>', 'exec')
            checks['syntax_valid'] = True
            checks['compiles'] = True

            # Check for bare excepts
            for node in ast.walk(tree):
                if not isinstance(node, ast.ExceptHandler):
                    continue

                if node.type is None:
                    checks['no_bare_except'] = False
                    feedback.append("Avoid bare 'except:' - catch specific exceptions")
                    break

        except SyntaxError as e:
            checks['syntax_valid'] = False
            checks['compiles'] = False
            feedback.append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            checks['compiles'] = False
            feedback.append(f"Compilation error: {str(e)}")

        return checks, feedback


class TestsValidator(BaseValidator):
    """
    WHY: Validate test code for proper structure and assertions.

    RESPONSIBILITY: Check tests have proper functions, assertions, and framework imports.
    """

    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """Validate test code."""
        checks = {}
        feedback = []

        # Check 1: Has test functions
        has_test_functions = bool(re.search(r'def test_\w+\(', code))
        checks['has_test_functions'] = has_test_functions

        if not has_test_functions:
            feedback.append("No test functions found (must start with 'test_')")

        # Check 2: Has assertions
        has_assertions = bool(re.search(r'assert\s+', code))
        checks['has_assertions'] = has_assertions

        if not has_assertions:
            feedback.append("No assertions found in tests")

        # Check 3: Imports test framework
        imports_test_framework = 'import pytest' in code or 'import unittest' in code
        checks['imports_test_framework'] = imports_test_framework

        if not imports_test_framework:
            feedback.append("Missing test framework import (pytest or unittest)")

        # Check 4: Parseable
        try:
            ast.parse(code)
            checks['parseable'] = True
        except SyntaxError as e:
            checks['parseable'] = False
            feedback.append(f"Test syntax error: {e.msg}")

        severity = "high"

        return checks, feedback, severity


class FullCodeValidator(BaseValidator):
    """
    WHY: Comprehensive validation combining all stage checks.

    RESPONSIBILITY: Run all validations and check overall code structure.
    """

    def __init__(self):
        """Initialize with all stage validators."""
        super().__init__()
        self.imports_validator = ImportsValidator()
        self.signature_validator = SignatureValidator()
        self.body_validator = BodyValidator()

    def validate(self, code: str, context: Optional[ValidationContext]) -> Tuple[Dict[str, bool], List[str], str]:
        """Validate complete code artifact."""
        checks = {}
        feedback = []

        # Run all stage validations
        import_checks, import_feedback, _ = self.imports_validator.validate(code, context)
        sig_checks, sig_feedback, _ = self.signature_validator.validate(code, context)
        body_checks, body_feedback, _ = self.body_validator.validate(code, context)

        checks.update(import_checks)
        checks.update(sig_checks)
        checks.update(body_checks)

        feedback.extend(import_feedback)
        feedback.extend(sig_feedback)
        feedback.extend(body_feedback)

        # Additional full-code checks
        structure_checks, structure_feedback = self._check_code_structure(code)
        checks.update(structure_checks)
        feedback.extend(structure_feedback)

        # Determine severity
        severity = self._determine_full_code_severity(checks)

        return checks, feedback, severity

    def _check_code_structure(self, code: str) -> Tuple[Dict[str, bool], List[str]]:
        """Check overall code structure."""
        checks = {}
        feedback = []

        # Check: File size reasonable
        line_count = ValidatorHelper.count_code_lines(code)
        checks['reasonable_size'] = 5 <= line_count <= 1000

        if line_count < 5:
            feedback.append("Code too short - likely incomplete")
        elif line_count > 1000:
            feedback.append("Code very long - consider splitting into modules")

        # Check: Has proper structure
        try:
            tree = ast.parse(code)
            has_structure = any(isinstance(n, (ast.FunctionDef, ast.ClassDef)) for n in tree.body)
            checks['has_structure'] = has_structure

            if not has_structure:
                feedback.append("Code has no functions or classes - likely incomplete")
        except:
            pass

        return checks, feedback

    def _determine_full_code_severity(self, checks: Dict[str, bool]) -> str:
        """Determine overall severity for full code."""
        # Guard: Check critical failures first
        if not checks.get('compiles', True) or not checks.get('parseable', True):
            return "critical"

        # Check for placeholder issues
        has_placeholder_issues = any('placeholder' in k for k, v in checks.items() if not v)

        if has_placeholder_issues:
            return "critical"

        return "medium"
