#!/usr/bin/env python3
"""
Module: Refactoring Suggestion Generator - Human-Readable Recommendations

WHY: Transforms raw code smell data into actionable, educational instructions
     for developers. Bridges gap between automated detection and human action.

RESPONSIBILITY:
    - Generate markdown-formatted refactoring instructions
    - Categorize suggestions by type
    - Include best practices and rationale
    - Merge code review feedback with automated suggestions
    - Prioritize suggestions by severity

PATTERNS:
    - Builder Pattern: Incrementally construct complex instruction text
    - Template Method: Consistent formatting across suggestion types
    - Strategy Pattern: Different formatters for different smell types
"""

from typing import List, Dict, Any, Optional, Callable
from .models import (
    RefactoringAnalysis,
    CodeSmell,
    PatternType,
    RefactoringPriority,
    LongMethodSmell,
    SimpleLoopSmell,
    IfElifChainSmell
)


class SuggestionFormatter:
    """
    Base class for formatting code smell suggestions.

    WHY: Provides consistent formatting interface across smell types.

    RESPONSIBILITY:
        - Define formatting contract
        - Provide default markdown formatting
    """

    def format_header(self, title: str) -> str:
        """Generate section header."""
        return f"## {title}\n"

    def format_suggestion(self, smell: CodeSmell) -> str:
        """
        Format a single code smell as markdown list item.

        WHY: Override in subclasses for type-specific formatting.
        """
        return f"- Line {smell.line_number}: {smell.suggestion}\n"


class LongMethodFormatter(SuggestionFormatter):
    """
    Formatter for long method suggestions.

    WHY: Includes method name and line count in output.
    """

    def format_suggestion(self, smell: LongMethodSmell) -> str:
        """Format long method with context."""
        method_name = smell.metadata.get('method_name', 'unknown')
        length = smell.metadata.get('method_length', 0)
        return f"- Line {smell.line_number}: {method_name} ({length} lines) - {smell.suggestion}\n"


class SimpleLoopFormatter(SuggestionFormatter):
    """
    Formatter for simple loop suggestions.

    WHY: Provides comprehension examples based on operation type.
    """

    def format_suggestion(self, smell: SimpleLoopSmell) -> str:
        """Format loop suggestion with operation context."""
        operation = smell.metadata.get('loop_operation', 'unknown')
        example = self._get_example(operation)
        return f"- Line {smell.line_number}: {smell.suggestion}{example}\n"

    def _get_example(self, operation: str) -> str:
        """
        Get comprehension example for operation type.

        WHY: Educational - shows developers the transformation.
        """
        examples = {
            'append': ' (e.g., [x for x in items])',
            'add': ' (e.g., {x for x in items})',
            'update': ' (e.g., {k: v for k, v in items})'
        }
        return examples.get(operation, '')


class IfElifChainFormatter(SuggestionFormatter):
    """
    Formatter for if/elif chain suggestions.

    WHY: Shows number of branches to help developers prioritize.
    """

    def format_suggestion(self, smell: IfElifChainSmell) -> str:
        """Format if/elif chain with branch count."""
        elif_count = smell.metadata.get('elif_count', 0)
        total_branches = elif_count + 1
        return f"- Line {smell.line_number}: {total_branches} branches - {smell.suggestion}\n"


class RefactoringSuggestionGenerator:
    """
    Generates comprehensive refactoring instruction documents.

    WHY: Transforms analysis results into actionable developer documentation.
         Provides educational context beyond just listing issues.

    RESPONSIBILITY:
        - Orchestrate suggestion formatting
        - Generate markdown documentation
        - Include best practices
        - Merge multiple feedback sources
        - Prioritize by severity

    PATTERN: Builder Pattern for instruction document construction
    """

    def __init__(self):
        """Initialize formatter dispatch table."""
        self._formatters: Dict[PatternType, SuggestionFormatter] = {
            PatternType.LONG_METHOD: LongMethodFormatter(),
            PatternType.LOOP: SimpleLoopFormatter(),
            PatternType.IF_ELIF: IfElifChainFormatter()
        }

    def generate_instructions(
        self,
        analysis: RefactoringAnalysis,
        code_review_issues: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate comprehensive refactoring instructions.

        WHY: Single method provides complete documentation, simplifying usage.

        Args:
            analysis: RefactoringAnalysis from analyzer
            code_review_issues: Optional code review feedback to merge

        Returns:
            Markdown-formatted instruction document
        """
        builder = InstructionBuilder(analysis)

        # Add header
        builder.add_header()

        # Add categorized suggestions
        builder.add_long_method_section(self._formatters[PatternType.LONG_METHOD])
        builder.add_simple_loop_section(self._formatters[PatternType.LOOP])
        builder.add_if_elif_section(self._formatters[PatternType.IF_ELIF])

        # Add code review feedback if provided
        if code_review_issues:
            builder.add_code_review_section(code_review_issues)

        # Add best practices
        builder.add_best_practices_section()

        return builder.build()


class InstructionBuilder:
    """
    Builder for constructing refactoring instruction documents.

    WHY: Separates document construction from formatting logic.
         Allows flexible instruction composition.

    RESPONSIBILITY:
        - Accumulate instruction sections
        - Maintain consistent markdown structure
        - Provide fluent interface for section addition

    PATTERN: Builder Pattern
    """

    def __init__(self, analysis: RefactoringAnalysis):
        """
        Initialize builder with analysis data.

        Args:
            analysis: RefactoringAnalysis to document
        """
        self.analysis = analysis
        self.sections: List[str] = []

    def add_header(self) -> 'InstructionBuilder':
        """Add document header with summary."""
        header = [
            "# Refactoring Instructions\n",
            f"File: {self.analysis.file_path}\n",
            f"Total Issues: {self.analysis.total_issues}\n\n"
        ]
        self.sections.extend(header)
        return self

    def add_long_method_section(self, formatter: SuggestionFormatter) -> 'InstructionBuilder':
        """
        Add long method suggestions section.

        WHY: Guard clause pattern - only add if methods exist.
        """
        # Guard: Skip empty sections
        if not self.analysis.long_methods:
            return self

        self.sections.append(formatter.format_header("Long Methods (Extract Helper Methods)"))

        for smell in self.analysis.long_methods:
            self.sections.append(formatter.format_suggestion(smell))

        self.sections.append("\n")
        return self

    def add_simple_loop_section(self, formatter: SuggestionFormatter) -> 'InstructionBuilder':
        """
        Add simple loop suggestions section.

        WHY: Guard clause prevents empty sections.
        """
        # Guard: Skip empty sections
        if not self.analysis.simple_loops:
            return self

        self.sections.append(formatter.format_header("Loops → Comprehensions"))

        for smell in self.analysis.simple_loops:
            self.sections.append(formatter.format_suggestion(smell))

        self.sections.append("\n")
        return self

    def add_if_elif_section(self, formatter: SuggestionFormatter) -> 'InstructionBuilder':
        """
        Add if/elif chain suggestions section.

        WHY: Guard clause prevents empty sections.
        """
        # Guard: Skip empty sections
        if not self.analysis.if_elif_chains:
            return self

        self.sections.append(formatter.format_header("If/Elif Chains → Dictionary Mapping"))

        for smell in self.analysis.if_elif_chains:
            self.sections.append(formatter.format_suggestion(smell))

        self.sections.append("\n")
        return self

    def add_code_review_section(self, issues: List[Dict[str, Any]]) -> 'InstructionBuilder':
        """
        Add code review issues section.

        WHY: Merges human and automated feedback in one document.

        Args:
            issues: List of code review issue dicts
        """
        # Guard: Skip if no issues
        if not issues:
            return self

        self.sections.append("## Code Review Issues to Fix\n")

        for issue in issues:
            severity = issue.get('severity', 'UNKNOWN')
            category = issue.get('category', 'Unknown')
            description = issue.get('description', 'No description')
            self.sections.append(f"- [{severity}] {category}: {description}\n")

        self.sections.append("\n")
        return self

    def add_best_practices_section(self) -> 'InstructionBuilder':
        """
        Add best practices reference section.

        WHY: Educational - helps developers understand the "why" behind suggestions.
        """
        best_practices = [
            "## Refactoring Best Practices\n",
            "1. Use list/dict/set comprehensions for simple loops\n",
            "2. Use next() with generator for first-match patterns\n",
            "3. Replace if/elif chains (3+ branches) with dict.get()\n",
            "4. Extract methods longer than 50 lines\n",
            "5. Use collections module: defaultdict, Counter, chain\n",
            "6. Prefer composition over inheritance\n",
            "7. Follow Single Responsibility Principle\n"
        ]
        self.sections.extend(best_practices)
        return self

    def build(self) -> str:
        """
        Build final instruction document.

        Returns:
            Complete markdown document
        """
        return "".join(self.sections)
