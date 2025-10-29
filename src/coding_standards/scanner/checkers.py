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


class PlaceholderImplementationChecker:
    """
    Checks for placeholder/incomplete implementations.

    WHY: Placeholder code can cause runtime failures when LLMs don't receive proper instructions.
    RESPONSIBILITY: Detect incomplete implementations, missing format specifications.
    PATTERNS: Strategy (detection strategy).
    """

    @staticmethod
    def check(
        node: ast.FunctionDef,
        file_path: str,
        source_lines: List[str]
    ) -> Optional[Violation]:
        """
        Check if function has placeholder implementation indicators.

        WHY: Incomplete prompts cause LLMs to return unexpected formats.

        Args:
            node: AST FunctionDef node to check
            file_path: File path for violation reporting
            source_lines: Source code lines for context

        Returns:
            Violation if placeholder found, None otherwise
        """
        # Get function source code
        func_start = node.lineno - 1
        func_end = node.end_lineno if hasattr(node, 'end_lineno') else func_start + 10
        func_lines = source_lines[func_start:func_end]
        func_source = '\n'.join(func_lines)

        # Pattern 1: Check for placeholder comments
        placeholder_patterns = [
            '# Simple',
            '(can be enhanced',
            '# Placeholder',
            '# TODO: implement',
            '# FIXME:',
            'NotImplemented',
        ]

        for pattern in placeholder_patterns:
            if pattern in func_source:
                context = _get_line_context(source_lines, node.lineno)
                return Violation(
                    file_path=file_path,
                    line_number=node.lineno,
                    violation_type='placeholder_implementation',
                    severity='critical',
                    message=f'Placeholder implementation detected: "{pattern}" - complete implementation required',
                    context=context
                )

        # Pattern 2: Check if function builds prompts but doesn't specify JSON format
        if 'prompt' in node.name.lower() or 'build' in node.name.lower():
            has_json_instruction = any(
                'JSON' in line or 'json' in line
                for line in func_lines
            )
            returns_string = any(
                'return' in line and ('f"""' in line or "f'''" in line or 'str(' in line)
                for line in func_lines
            )

            if returns_string and not has_json_instruction:
                context = _get_line_context(source_lines, node.lineno)
                return Violation(
                    file_path=file_path,
                    line_number=node.lineno,
                    violation_type='missing_format_specification',
                    severity='warning',
                    message=f'Prompt builder "{node.name}" does not specify expected JSON response format',
                    context=context
                )

        return None


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
