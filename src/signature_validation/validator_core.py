#!/usr/bin/env python3
"""
Signature Validator Core Orchestration

WHY: Main validation orchestration and coordination
RESPONSIBILITY: Coordinate all validation stages and provide public API
PATTERNS: Facade pattern, template method pattern
"""

import ast
from pathlib import Path
from typing import List, Dict, Set, Optional
from signature_validation.models import SignatureIssue, FunctionInfo
from signature_validation.signature_extractor import SignatureExtractor
from signature_validation.parameter_validator import ParameterValidator, ReturnTypeValidator


class EnhancedSignatureValidator:
    """
    Enhanced validator for function signatures, types, and return values

    WHY: Provides comprehensive static analysis including:
    - Parameter count validation
    - Type hint checking
    - Return type validation
    - Dynamic call pattern detection

    RESPONSIBILITY: Orchestrate all validation components
    PATTERNS: Facade pattern, template method pattern
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the enhanced validator

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.issues: List[SignatureIssue] = []
        self.function_info: Dict[str, FunctionInfo] = {}

    def validate_file(self, file_path: str) -> List[SignatureIssue]:
        """
        Validate function call signatures and types in a Python file

        WHY: Main entry point for file validation
        RESPONSIBILITY: Orchestrate multi-pass validation
        PATTERNS: Template method pattern

        Args:
            file_path: Path to Python file to validate

        Returns:
            List of SignatureIssue objects
        """
        self.issues = []
        self.function_info = {}

        # Guard clause: file doesn't exist
        if not Path(file_path).exists():
            return self.issues

        try:
            source = self._read_file(file_path)
            tree = ast.parse(source, filename=file_path)

            # Pass 1: Collect function definitions with type hints
            self._collect_function_signatures(tree)

            # Pass 2: Validate function calls
            self._validate_function_calls(tree, file_path)

            # Pass 3: Validate return types
            self._validate_return_types(file_path)

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

        WHY: Batch validation for entire projects
        RESPONSIBILITY: Recursive directory traversal and validation
        PATTERNS: Iterator pattern with filtering

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

    def _read_file(self, file_path: str) -> str:
        """
        Read file contents

        WHY: Centralize file reading for error handling
        RESPONSIBILITY: Load source code safely
        PATTERNS: Guard clause for encoding errors

        Args:
            file_path: Path to file

        Returns:
            File contents as string
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _collect_function_signatures(self, tree: ast.AST) -> None:
        """
        Collect function signatures from AST

        WHY: Build complete signature database
        RESPONSIBILITY: Extract all function metadata
        PATTERNS: Delegation to specialized component

        Args:
            tree: AST root node
        """
        extractor = SignatureExtractor()
        self.function_info = extractor.extract_from_tree(tree)

    def _validate_function_calls(self, tree: ast.AST, file_path: str) -> None:
        """
        Validate all function calls in AST

        WHY: Check parameter usage across entire file
        RESPONSIBILITY: Coordinate call validation
        PATTERNS: Visitor pattern with delegation

        Args:
            tree: AST root node
            file_path: Source file path
        """
        validator = ParameterValidator(self.function_info, self.verbose)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                issues = validator.validate_call(node, file_path)
                self.issues.extend(issues)

    def _validate_return_types(self, file_path: str) -> None:
        """
        Validate return types for all functions

        WHY: Ensure return type correctness
        RESPONSIBILITY: Coordinate return type validation
        PATTERNS: Delegation to specialized component

        Args:
            file_path: Source file path
        """
        validator = ReturnTypeValidator(self.function_info, self.verbose)
        issues = validator.validate_returns(file_path)
        self.issues.extend(issues)
