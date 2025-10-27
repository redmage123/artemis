#!/usr/bin/env python3
"""
Module: Code Refactoring Agent - Automated Code Quality Improvements

Purpose: Analyzes Python code and identifies refactoring opportunities to improve
         code quality, maintainability, and adherence to best practices.

Why: Post-review refactoring ensures code meets quality standards before merge.
     Automated detection of common anti-patterns saves developers time and
     improves code consistency across the codebase.

Patterns: Strategy Pattern (different refactoring strategies), Visitor Pattern (AST traversal)

Integration: Works with code review agent output to apply suggested improvements.
            Uses Python's ast module to analyze code structure without execution.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RefactoringRule:
    """
    Represents a single refactoring pattern rule.

    Why it exists: Encapsulates refactoring metadata for prioritization and tracking.
    Design pattern: Value Object - immutable data container.

    Attributes:
        name: Unique identifier for the refactoring rule
        pattern_type: Category ('loop', 'if_elif', 'long_method', 'duplication')
        description: Human-readable explanation of the refactoring
        priority: Urgency level (1=critical, 2=high, 3=medium, 4=low)
    """
    name: str
    pattern_type: str  # 'loop', 'if_elif', 'long_method', 'duplication'
    description: str
    priority: int  # 1=critical, 2=high, 3=medium, 4=low


class CodeRefactoringAgent:
    """
    Automated code refactoring agent for Python codebases.

    What this class does: Analyzes Python source files using AST parsing to identify
    common anti-patterns and suggest Pythonic improvements.

    Why it exists: Bridges the gap between code review feedback and actual implementation.
    Automates mechanical refactoring suggestions so developers can focus on logic.

    Design pattern: Visitor Pattern for AST traversal, Strategy Pattern for refactoring rules.

    Responsibilities:
    - Parse Python source code into AST
    - Detect anti-patterns (long methods, simple loops, if/elif chains)
    - Generate actionable refactoring instructions
    - Prioritize refactorings by impact
    - Provide educational context for suggested changes
    """

    REFACTORING_RULES = [
        RefactoringRule(
            name="loop_to_comprehension",
            pattern_type="loop",
            description="Convert simple for loops to list/dict comprehensions",
            priority=2
        ),
        RefactoringRule(
            name="if_elif_to_mapping",
            pattern_type="if_elif",
            description="Convert long if/elif chains to dictionary mapping",
            priority=2
        ),
        RefactoringRule(
            name="extract_long_method",
            pattern_type="long_method",
            description="Extract methods longer than 50 lines",
            priority=1
        ),
        RefactoringRule(
            name="use_next_for_first_match",
            pattern_type="loop",
            description="Use next() with generator for first-match patterns",
            priority=3
        ),
        RefactoringRule(
            name="use_collections_module",
            pattern_type="loop",
            description="Use defaultdict, Counter, chain from collections",
            priority=3
        ),
    ]

    def __init__(self, logger=None, verbose: bool = True):
        """
        Initialize refactoring agent.

        What this method does: Sets up the agent with logging configuration.

        Why needed: Dependency injection for logger allows flexible logging backends.

        Args:
            logger: Optional logger instance for structured logging.
                   If None, uses simple print statements.
            verbose: Enable verbose logging to track refactoring analysis progress.
                    Useful for debugging but can be noisy in production.

        Returns:
            None - modifies instance state only.

        Raises:
            No exceptions raised - this is a simple initialization.
        """
        self.logger = logger
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message with optional severity level.

        What this method does: Conditionally logs messages based on verbosity setting.

        Why needed: Provides consistent logging interface regardless of logger backend.
        Respects user's preference for verbosity to avoid log spam.

        Args:
            message: The log message text to output
            level: Severity level (INFO, WARNING, ERROR) for log filtering

        Returns:
            None - side effect only (logging)

        Raises:
            No exceptions - logging failures are silently ignored to avoid
            disrupting refactoring analysis.
        """
        if self.verbose:
            if self.logger:
                self.logger.log(message, level)
            else:
                print(f"[Refactoring] {message}")

    def analyze_file_for_refactoring(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Python file for refactoring opportunities using AST parsing.

        What this method does: Parses Python source into AST and runs multiple
        analyzers to detect anti-patterns (long methods, simple loops, if/elif chains).

        Why needed: Central orchestration point for all refactoring analysis.
        Separates concerns - this method coordinates, individual methods analyze.

        Args:
            file_path: Path object pointing to Python source file.
                      Must be readable and contain valid Python syntax.

        Returns:
            Dict containing:
                - 'file': str path to analyzed file
                - 'long_methods': List[Dict] of methods exceeding 50 lines
                - 'simple_loops': List[Dict] of for loops that could be comprehensions
                - 'if_elif_chains': List[Dict] of if/elif chains (3+ branches)
                - 'total_issues': int count of all detected issues
                - 'error': str (only if parsing fails)

        Raises:
            No exceptions raised - errors are caught and returned in result dict.
            This design prevents one bad file from stopping batch analysis.
        """
        self.log(f"Analyzing {file_path.name} for refactoring opportunities...")

        try:
            with open(file_path, 'r') as f:
                source = f.read()
                tree = ast.parse(source)

            suggestions = {
                'file': str(file_path),
                'long_methods': self._find_long_methods(tree),
                'simple_loops': self._find_simple_loops(tree, source),
                'if_elif_chains': self._find_if_elif_chains(tree, source),
                'total_issues': 0
            }

            suggestions['total_issues'] = (
                len(suggestions['long_methods']) +
                len(suggestions['simple_loops']) +
                len(suggestions['if_elif_chains'])
            )

            return suggestions

        except Exception as e:
            self.log(f"Error analyzing {file_path}: {e}", "ERROR")
            return {'file': str(file_path), 'error': str(e), 'total_issues': 0}

    def _find_long_methods(self, tree: ast.AST) -> List[Dict]:
        """
        Find methods longer than 50 lines that violate Single Responsibility Principle.

        What this method does: Traverses AST to find FunctionDef nodes and measures
        their line count. Flags methods exceeding the 50-line threshold.

        Why needed: Long methods are harder to test, understand, and maintain.
        The 50-line threshold is a common industry best practice for maintainability.

        Args:
            tree: Python AST (Abstract Syntax Tree) from ast.parse()

        Returns:
            List of dicts, each containing:
                - 'name': Function name
                - 'line': Starting line number
                - 'length': Total lines in function
                - 'suggestion': Refactoring recommendation

        Raises:
            No exceptions - malformed AST nodes are silently skipped to handle
            edge cases in Python syntax gracefully.
        """
        long_methods = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        long_methods.append({
                            'name': node.name,
                            'line': node.lineno,
                            'length': length,
                            'suggestion': f'Extract helper methods from {node.name} ({length} lines)'
                        })

        return long_methods

    def _find_simple_loops(self, tree: ast.AST, source: str) -> List[Dict]:
        """
        Find simple for loops that can be converted to list/dict comprehensions.

        What this method does: Identifies for loops with single-statement bodies
        that perform simple append/add operations - prime candidates for Pythonic
        comprehensions.

        Why needed: List comprehensions are:
        - More readable (express intent clearly)
        - Faster (optimized C implementation)
        - More Pythonic (idiomatic code)

        Args:
            tree: Python AST to analyze
            source: Original source code (currently unused but available for context)

        Returns:
            List of dicts with:
                - 'line': Line number of the for loop
                - 'suggestion': Recommendation to use comprehension

        Raises:
            No exceptions - silently skips complex loops that don't match pattern.
        """
        simple_loops = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if loop body is simple (append, extend, etc.)
                if len(node.body) == 1:
                    stmt = node.body[0]
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        if isinstance(stmt.value.func, ast.Attribute):
                            method_name = stmt.value.func.attr
                            if method_name in ['append', 'add', 'update']:
                                simple_loops.append({
                                    'line': node.lineno,
                                    'suggestion': f'Convert for loop to list/set/dict comprehension'
                                })

        return simple_loops

    def _find_if_elif_chains(self, tree: ast.AST, source: str) -> List[Dict]:
        """
        Find long if/elif chains (3+ branches) that should use dictionary mapping.

        What this method does: Traverses AST to find If nodes with multiple elif
        branches. Counts branches and flags chains with 3+ branches as candidates
        for dict.get() refactoring.

        Why needed: Long if/elif chains:
        - Are harder to maintain (must update in multiple places)
        - Perform slower (linear search vs constant-time dict lookup)
        - Are less Pythonic (dict dispatch is more idiomatic)

        Example transformation:
            # Before
            if x == 'a': return 1
            elif x == 'b': return 2
            elif x == 'c': return 3

            # After
            mapping = {'a': 1, 'b': 2, 'c': 3}
            return mapping.get(x, default)

        Args:
            tree: Python AST to analyze
            source: Original source code (currently unused)

        Returns:
            List of dicts with:
                - 'line': Line number of if statement
                - 'elif_count': Number of elif branches
                - 'suggestion': Recommendation to use dictionary

        Raises:
            No exceptions - malformed if/else structures are skipped.
        """
        if_elif_chains = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Count elif branches
                elif_count = 0
                current = node
                while hasattr(current, 'orelse') and len(current.orelse) == 1:
                    if isinstance(current.orelse[0], ast.If):
                        elif_count += 1
                        current = current.orelse[0]
                    else:
                        break

                # If 3+ elif branches, suggest dictionary
                if elif_count >= 3:
                    if_elif_chains.append({
                        'line': node.lineno,
                        'elif_count': elif_count,
                        'suggestion': f'Convert {elif_count+1}-branch if/elif to dictionary mapping'
                    })

        return if_elif_chains

    def generate_refactoring_instructions(
        self,
        analysis: Dict[str, Any],
        code_review_issues: List[Dict] = None
    ) -> str:
        """
        Generate detailed, actionable refactoring instructions for developers.

        What this method does: Transforms raw analysis data into human-readable
        markdown format with categorized issues and best practice recommendations.

        Why needed: Bridges the gap between automated detection and human action.
        Provides educational context so developers understand WHY to refactor,
        not just WHAT to refactor.

        Args:
            analysis: Dict from analyze_file_for_refactoring() containing:
                - long_methods, simple_loops, if_elif_chains lists
                - file path and total issue count
            code_review_issues: Optional list of code review findings to merge.
                Allows combining automated and human review feedback.

        Returns:
            Markdown-formatted string with:
                - File header and issue count
                - Categorized refactoring suggestions
                - Code review issues (if provided)
                - Best practices summary

        Raises:
            No exceptions - missing data results in empty sections rather than errors.
        """
        instructions = []

        instructions.append("# Refactoring Instructions\n")
        instructions.append(f"File: {analysis['file']}\n")
        instructions.append(f"Total Issues: {analysis['total_issues']}\n\n")

        # Long methods
        if analysis.get('long_methods'):
            instructions.append("## Long Methods (Extract Helper Methods)\n")
            for method in analysis['long_methods']:
                instructions.append(f"- Line {method['line']}: {method['suggestion']}\n")
            instructions.append("\n")

        # Simple loops
        if analysis.get('simple_loops'):
            instructions.append("## Loops → Comprehensions\n")
            for loop in analysis['simple_loops']:
                instructions.append(f"- Line {loop['line']}: {loop['suggestion']}\n")
            instructions.append("\n")

        # If/elif chains
        if analysis.get('if_elif_chains'):
            instructions.append("## If/Elif Chains → Dictionary Mapping\n")
            for chain in analysis['if_elif_chains']:
                instructions.append(f"- Line {chain['line']}: {chain['suggestion']}\n")
            instructions.append("\n")

        # Add code review issues if provided
        if code_review_issues:
            instructions.append("## Code Review Issues to Fix\n")
            for issue in code_review_issues:
                severity = issue.get('severity', 'UNKNOWN')
                category = issue.get('category', 'Unknown')
                description = issue.get('description', 'No description')
                instructions.append(f"- [{severity}] {category}: {description}\n")
            instructions.append("\n")

        # Add best practices
        instructions.append("## Refactoring Best Practices\n")
        instructions.append("1. Use list/dict/set comprehensions for simple loops\n")
        instructions.append("2. Use next() with generator for first-match patterns\n")
        instructions.append("3. Replace if/elif chains (3+ branches) with dict.get()\n")
        instructions.append("4. Extract methods longer than 50 lines\n")
        instructions.append("5. Use collections module: defaultdict, Counter, chain\n")
        instructions.append("6. Prefer composition over inheritance\n")
        instructions.append("7. Follow Single Responsibility Principle\n")

        return "".join(instructions)

    def apply_automated_refactoring(
        self,
        file_path: Path,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply automated refactoring to a file (currently suggestions-only).

        What this method does: Placeholder for future automated AST transformation.
        Currently returns suggestions without modifying source code.

        Why needed: Future-proofs the API for when we implement automated refactoring.
        Keeps interface consistent - same method signature whether suggesting or applying.

        WHY NOT IMPLEMENTED YET: Automated AST transformation is risky:
        - May break code semantics (especially with complex Python features)
        - Requires extensive testing to ensure correctness
        - Better to provide suggestions and let developers review changes

        Args:
            file_path: Path to Python file to refactor
            analysis: Analysis results from analyze_file_for_refactoring()

        Returns:
            Dict with:
                - 'file': str path
                - 'status': 'SUGGESTIONS_ONLY'
                - 'message': Explanation of why automation is limited
                - 'suggestions': Copy of analysis for reference

        Raises:
            No exceptions - this is a no-op wrapper for future functionality.
        """
        self.log(f"Applying automated refactoring to {file_path.name}...")

        # For now, return suggestions only
        # Full automation would require AST transformation
        return {
            'file': str(file_path),
            'status': 'SUGGESTIONS_ONLY',
            'message': 'Automated refactoring requires LLM or manual intervention',
            'suggestions': analysis
        }


def create_refactoring_agent(logger=None, verbose: bool = True) -> CodeRefactoringAgent:
    """
    Factory function to create refactoring agent instance.

    What this function does: Creates and returns a configured CodeRefactoringAgent.

    Why needed: Factory pattern provides a consistent creation interface and
    allows future extensions (e.g., configuration file support) without changing
    client code.

    Args:
        logger: Optional logger for tracking refactoring operations.
               Defaults to None (uses print statements).
        verbose: Enable detailed logging of analysis steps.
                Recommended for development, disable in production.

    Returns:
        Fully initialized CodeRefactoringAgent ready for use.

    Raises:
        No exceptions - initialization is simple and cannot fail.
    """
    return CodeRefactoringAgent(logger=logger, verbose=verbose)


if __name__ == "__main__":
    # Example usage
    import sys

    agent = create_refactoring_agent()

    # Analyze this file
    file_path = Path(__file__)
    analysis = agent.analyze_file_for_refactoring(file_path)

    print("\nRefactoring Analysis:")
    print(f"File: {analysis['file']}")
    print(f"Total Issues: {analysis['total_issues']}")

    if analysis.get('long_methods'):
        print(f"\nLong Methods: {len(analysis['long_methods'])}")
        for method in analysis['long_methods']:
            print(f"  - {method['name']} ({method['length']} lines)")

    # Generate instructions
    instructions = agent.generate_refactoring_instructions(analysis)
    print("\n" + instructions)
