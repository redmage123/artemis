#!/usr/bin/env python3
"""
Function Signature Extraction

WHY: Parse and collect function signatures from AST
RESPONSIBILITY: Extract complete function metadata including type hints
PATTERNS: Visitor pattern, builder pattern for function info construction
"""

import ast
from typing import Dict
from signature_validation.models import FunctionInfo
from signature_validation.type_validator import TypeChecker


class SignatureExtractor:
    """
    Extract function signatures from AST

    WHY: Comprehensive function signature parsing
    RESPONSIBILITY: Build complete function metadata from AST
    PATTERNS: Visitor pattern, builder pattern
    """

    def __init__(self):
        """Initialize signature extractor"""
        self.type_checker = TypeChecker()
        self.function_info: Dict[str, FunctionInfo] = {}

    def extract_from_tree(self, tree: ast.AST) -> Dict[str, FunctionInfo]:
        """
        Extract all function signatures from AST

        WHY: Collect comprehensive function information for validation
        RESPONSIBILITY: Parse entire AST for function definitions
        PATTERNS: Visitor pattern

        Args:
            tree: AST root node

        Returns:
            Dictionary mapping function names to FunctionInfo
        """
        self.function_info = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._extract_function_info(node)

        return self.function_info

    def _extract_function_info(self, node: ast.FunctionDef) -> None:
        """
        Extract complete function information from function definition

        WHY: Build comprehensive function metadata
        RESPONSIBILITY: Parse all aspects of function signature
        PATTERNS: Builder pattern

        Args:
            node: Function definition AST node
        """
        func_info = FunctionInfo(name=node.name)

        # Extract regular arguments with type hints
        self._extract_regular_args(node, func_info)

        # Extract defaults
        func_info.defaults = node.args.defaults

        # Extract keyword-only arguments
        self._extract_kwonly_args(node, func_info)

        # Extract keyword-only defaults
        func_info.kwdefaults = node.args.kw_defaults

        # Check for *args and **kwargs
        func_info.has_varargs = node.args.vararg is not None
        func_info.has_varkw = node.args.kwarg is not None

        # Extract return type hint
        self._extract_return_type(node, func_info)

        # Collect return statements
        self._collect_return_statements(node, func_info)

        self.function_info[node.name] = func_info

    def _extract_regular_args(
        self,
        node: ast.FunctionDef,
        func_info: FunctionInfo
    ) -> None:
        """
        Extract regular arguments with type hints

        WHY: Parse positional and keyword arguments
        RESPONSIBILITY: Build argument list with types
        PATTERNS: Builder pattern

        Args:
            node: Function definition node
            func_info: Function info to populate
        """
        for arg in node.args.args:
            func_info.args.append(arg.arg)
            self._extract_type_hint(arg, func_info)

    def _extract_kwonly_args(
        self,
        node: ast.FunctionDef,
        func_info: FunctionInfo
    ) -> None:
        """
        Extract keyword-only arguments with type hints

        WHY: Parse keyword-only parameters
        RESPONSIBILITY: Build kwonly argument list with types
        PATTERNS: Builder pattern

        Args:
            node: Function definition node
            func_info: Function info to populate
        """
        for arg in node.args.kwonlyargs:
            func_info.kwonly.append(arg.arg)
            self._extract_type_hint(arg, func_info)

    def _extract_type_hint(self, arg: ast.arg, func_info: FunctionInfo) -> None:
        """
        Extract type hint from argument and store in function info

        WHY: Capture type annotations for validation
        RESPONSIBILITY: Parse and store type hints
        PATTERNS: Guard clause for early return

        Args:
            arg: Argument AST node
            func_info: Function info to populate
        """
        # Guard clause: no annotation
        if not arg.annotation:
            return

        type_str = self.type_checker.extract_type_from_annotation(arg.annotation)

        # Guard clause: extraction failed
        if not type_str:
            return

        func_info.arg_types[arg.arg] = type_str

    def _extract_return_type(
        self,
        node: ast.FunctionDef,
        func_info: FunctionInfo
    ) -> None:
        """
        Extract return type hint from function definition

        WHY: Capture return type for validation
        RESPONSIBILITY: Parse return type annotation
        PATTERNS: Guard clause for early return

        Args:
            node: Function definition node
            func_info: Function info to populate
        """
        # Guard clause: no return annotation
        if not node.returns:
            return

        return_type = self.type_checker.extract_type_from_annotation(node.returns)

        # Guard clause: extraction failed
        if not return_type:
            return

        func_info.return_type = return_type

    def _collect_return_statements(
        self,
        node: ast.FunctionDef,
        func_info: FunctionInfo
    ) -> None:
        """
        Collect all return statements for return type validation

        WHY: Track return statements for type checking
        RESPONSIBILITY: Find all return nodes in function
        PATTERNS: Visitor pattern

        Args:
            node: Function definition node
            func_info: Function info to populate
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                func_info.return_nodes.append(child)
