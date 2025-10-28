#!/usr/bin/env python3
"""
WHY: Implement specific code pattern checks
RESPONSIBILITY: Check for nested ifs and elif chains
PATTERNS: Strategy (pluggable checks)

Checkers detect specific code pattern violations.
"""

import ast
from typing import List, Optional
from coding_standards.scanner.models import Violation


class NestedIfChecker:
    """
    Checks for nested if statements.

    WHY: Nested ifs increase complexity, early returns are preferred.
    RESPONSIBILITY: Detect and report nested if violations.
    PATTERNS: Strategy (detection strategy).
    """

    @staticmethod
    def check(
        node: ast.If,
        file_path: str,
        source_lines: List[str]
    ) -> Optional[Violation]:
        """
        Check if node is a nested if statement (2+ levels deep).

        WHY: Guard clause pattern preferred over nesting.

        Args:
            node: AST If node to check
            file_path: File path for violation reporting
            source_lines: Source code lines for context

        Returns:
            Violation if nested, None otherwise
        """
        # Count nesting depth by walking up the tree
        depth = 0
        parent = getattr(node, 'parent', None)

        while parent:
            if isinstance(parent, ast.If):
                depth += 1
            parent = getattr(parent, 'parent', None)

        # Guard clause - not nested deeply enough
        if depth < 2:
            return None

        # Create violation for critical nesting
        context = _get_line_context(source_lines, node.lineno)
        return Violation(
            file_path=file_path,
            line_number=node.lineno,
            violation_type='nested_if',
            severity='critical',
            message=f'Nested if at depth {depth} - use early returns instead',
            context=context
        )


class ElifChainChecker:
    """
    Checks for long if/elif chains.

    WHY: Long chains suggest need for strategy pattern or dispatch table.
    RESPONSIBILITY: Detect and report elif chain violations.
    PATTERNS: Strategy (detection strategy).
    """

    @staticmethod
    def check(
        node: ast.If,
        file_path: str,
        source_lines: List[str]
    ) -> Optional[Violation]:
        """
        Check if node starts a long if/elif chain (3+ branches).

        WHY: Dispatch tables or strategy pattern preferred over long chains.

        Args:
            node: AST If node to check
            file_path: File path for violation reporting
            source_lines: Source code lines for context

        Returns:
            Violation if long chain, None otherwise
        """
        # Count elif branches
        elif_count = 0
        current = node

        while hasattr(current, 'orelse') and current.orelse:
            if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                elif_count += 1
                current = current.orelse[0]
            else:
                break

        # Guard clause - chain not long enough
        if elif_count < 2:
            return None

        # Create violation for long chain
        context = _get_line_context(source_lines, node.lineno)
        return Violation(
            file_path=file_path,
            line_number=node.lineno,
            violation_type='elif_chain',
            severity='warning',
            message=f'If/elif chain with {elif_count + 1} branches - consider strategy pattern or dict mapping',
            context=context
        )


def _get_line_context(source_lines: List[str], line_no: int, context_lines: int = 2) -> str:
    """
    Get source code context around a line.

    WHY: Context helps developers locate and understand violations.

    Args:
        source_lines: All source code lines
        line_no: Line number (1-indexed)
        context_lines: Lines of context before/after

    Returns:
        Formatted context string
    """
    start = max(0, line_no - context_lines - 1)
    end = min(len(source_lines), line_no + context_lines)

    lines = []
    for i in range(start, end):
        prefix = ">>> " if i == line_no - 1 else "    "
        lines.append(f"{prefix}{source_lines[i]}")

    return "\n".join(lines)
