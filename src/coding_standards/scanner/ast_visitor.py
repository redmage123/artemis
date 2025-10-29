#!/usr/bin/env python3
"""
WHY: Walk AST to detect code pattern violations
RESPONSIBILITY: Visit AST nodes and apply checkers
PATTERNS: Visitor (AST traversal), Strategy (pluggable checkers)

AST visitor enables accurate code pattern detection.
"""

import ast
from typing import List
from coding_standards.scanner.models import Violation
from coding_standards.scanner.checkers import (
    NestedIfChecker,
    ElifChainChecker,
    PlaceholderImplementationChecker
)


class CodeStandardsVisitor(ast.NodeVisitor):
    """
    AST visitor that detects coding standards violations.

    WHY: AST analysis provides accurate pattern detection.
    RESPONSIBILITY: Visit nodes, apply checkers, collect violations.
    PATTERNS: Visitor (traversal), Strategy (pluggable checkers).
    """

    def __init__(self, file_path: str, source_lines: List[str]):
        """
        Initialize visitor.

        Args:
            file_path: File path for violation reporting
            source_lines: Source code lines for context
        """
        self.file_path = file_path
        self.source_lines = source_lines
        self.violations: List[Violation] = []
        self.in_function = False

    def visit_FunctionDef(self, node):
        """
        Track function entry for context and check for placeholder implementations.

        WHY: Detect incomplete implementations and missing format specifications.

        Args:
            node: Function definition node
        """
        self.in_function = True

        # Check for placeholder implementations
        violation = PlaceholderImplementationChecker.check(node, self.file_path, self.source_lines)
        if violation:
            self.violations.append(violation)

        self.generic_visit(node)
        self.in_function = False

    def visit_If(self, node):
        """
        Detect nested if statements and if/elif chains.

        WHY: Multiple violation types can occur at if statements.

        Args:
            node: If node to check
        """
        # Check for nested ifs
        violation = NestedIfChecker.check(node, self.file_path, self.source_lines)
        if violation:
            self.violations.append(violation)

        # Check for elif chains
        violation = ElifChainChecker.check(node, self.file_path, self.source_lines)
        if violation:
            self.violations.append(violation)

        self.generic_visit(node)
