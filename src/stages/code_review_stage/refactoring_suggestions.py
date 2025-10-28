#!/usr/bin/env python3
"""
Code Review Stage - Refactoring Suggestions Generator

WHY: Separate suggestion generation logic from review execution for better testability.
RESPONSIBILITY: Generate actionable refactoring suggestions based on review failures.
PATTERNS: Builder pattern for constructing suggestions, Strategy pattern for suggestion types.

This module generates comprehensive refactoring suggestions when code reviews fail,
including standard best practices and RAG-based recommendations.
"""

from typing import List, Dict, Optional
from rag_agent import RAGAgent


class RefactoringSuggestionsGenerator:
    """
    Generator for refactoring suggestions based on code review failures.

    WHY: Provide actionable guidance to developers on how to fix review failures.
    RESPONSIBILITY: Build comprehensive refactoring suggestions from multiple sources.
    PATTERNS: Builder pattern for suggestion construction.

    Attributes:
        rag: Optional RAG agent for retrieving additional patterns
        logger: Logger interface for debug logging
    """

    # Standard refactoring recommendations (DRY - defined once)
    STANDARD_REFACTORINGS = [
        "### Required Refactorings:",
        "1. **Extract Long Methods**: Break down methods longer than 50 lines",
        "2. **Reduce Complexity**: Simplify nested if/else chains using guard clauses",
        "3. **Remove Code Duplication**: Apply DRY principle",
        "4. **Improve Naming**: Use descriptive, meaningful names for variables and methods",
        "5. **Add Error Handling**: Properly handle all error cases",
        "6. **Security Fixes**: Address all OWASP Top 10 vulnerabilities",
        "7. **Apply Design Patterns**: Use Strategy, Builder, or Null Object patterns where appropriate",
        "8. **Type Safety**: Add type hints and perform proper type checking",
        "9. **Documentation**: Add comprehensive docstrings and comments",
        "10. **SOLID Principles**: Ensure Single Responsibility, Open/Closed, etc.\n"
    ]

    # General best practices (DRY - defined once)
    BEST_PRACTICES = [
        "\n## General Best Practices",
        "- Follow language-specific idioms and conventions",
        "- Keep methods focused on a single responsibility",
        "- Prefer composition over inheritance",
        "- Use dependency injection for better testability",
        "- Write self-documenting code",
        "- Add unit tests for all refactored code",
        "- Ensure all tests pass after refactoring\n"
    ]

    def __init__(
        self,
        rag: Optional[RAGAgent],
        logger: 'LoggerInterface'
    ):
        """
        Initialize suggestions generator.

        Args:
            rag: Optional RAG agent for retrieving patterns
            logger: Logger interface
        """
        self.rag = rag
        self.logger = logger

    def generate_suggestions(
        self,
        review_results: List[Dict],
        card_id: str,
        task_title: str
    ) -> str:
        """
        Generate refactoring suggestions based on code review failures.

        WHY: Provide actionable guidance when reviews fail.
        PATTERNS: Builder pattern - construct suggestions step by step.

        Args:
            review_results: List of review results from all developers
            card_id: Task card identifier
            task_title: Task title

        Returns:
            Complete refactoring suggestions text
        """
        self.logger.log(
            "🔧 Generating refactoring suggestions based on code review failures...",
            "INFO"
        )

        suggestions = []
        suggestions.extend(self._build_header(task_title, card_id))
        suggestions.extend(self._build_developer_suggestions(review_results))
        suggestions.extend(self.BEST_PRACTICES)
        suggestions.extend(self._build_rag_suggestions())

        suggestion_text = "\n".join(suggestions)
        self.logger.log(
            f"✅ Generated {len(suggestions)} lines of refactoring suggestions",
            "INFO"
        )

        return suggestion_text

    def _build_header(self, task_title: str, card_id: str) -> List[str]:
        """
        Build header section for refactoring suggestions.

        WHY: Provide context about what needs refactoring.

        Args:
            task_title: Task title
            card_id: Task card identifier

        Returns:
            List of header lines
        """
        return [
            "# REFACTORING INSTRUCTIONS FOR CODE REVIEW FAILURES\n",
            f"**Task**: {task_title}",
            f"**Card ID**: {card_id}\n",
            "The following refactorings are required to pass code review:\n"
        ]

    def _build_developer_suggestions(
        self,
        review_results: List[Dict]
    ) -> List[str]:
        """
        Build developer-specific refactoring suggestions.

        WHY: Provide targeted guidance for each failing implementation.
        PATTERNS: Filter pattern - only include failed/needs improvement reviews.

        Args:
            review_results: List of review results

        Returns:
            List of developer-specific suggestion lines
        """
        suggestions = []

        # Filter to only failed/needs improvement reviews
        failing_reviews = [
            r for r in review_results
            if r.get('review_status', 'UNKNOWN') in ["FAIL", "NEEDS_IMPROVEMENT"]
        ]

        for result in failing_reviews:
            suggestions.extend(
                self._build_single_developer_suggestion(result)
            )

        return suggestions

    def _build_single_developer_suggestion(
        self,
        result: Dict
    ) -> List[str]:
        """
        Build suggestion for a single developer.

        WHY: DRY - extract repeated logic for single developer.

        Args:
            result: Review result dictionary

        Returns:
            List of suggestion lines for this developer
        """
        developer_name = result.get('review_result', {}).get('developer_name', 'unknown')
        review_status = result.get('review_status', 'UNKNOWN')
        critical_issues = result.get('critical_issues', 0)
        high_issues = result.get('high_issues', 0)

        suggestions = [
            f"\n## {developer_name} - Refactoring Required",
            f"Status: {review_status}",
            f"Critical Issues: {critical_issues}",
            f"High Issues: {high_issues}\n"
        ]

        suggestions.extend(self.STANDARD_REFACTORINGS)

        return suggestions

    def _build_rag_suggestions(self) -> List[str]:
        """
        Query RAG for additional refactoring patterns.

        WHY: Leverage past experience to provide context-specific suggestions.
        PERFORMANCE: Limits to top 3 results to keep suggestions focused.

        Returns:
            List of RAG-based suggestion lines
        """
        if not self.rag:
            return []

        try:
            rag_results = self.rag.query_similar(
                query_text="refactoring patterns code quality best practices",
                artifact_type="architecture_decision",
                top_k=3
            )

            if not rag_results:
                return []

            return self._format_rag_results(rag_results)

        except Exception as e:
            self.logger.log(
                f"Could not query RAG for additional patterns: {e}",
                "WARNING"
            )
            return []

    def _format_rag_results(self, rag_results: List[Dict]) -> List[str]:
        """
        Format RAG query results into suggestion lines.

        WHY: DRY - extract formatting logic.
        PERFORMANCE: Truncates long content to 500 chars for readability.

        Args:
            rag_results: List of RAG query results

        Returns:
            List of formatted suggestion lines
        """
        suggestions = ["\n## Additional Refactoring Patterns from Knowledge Base"]

        for i, result in enumerate(rag_results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            refactoring_type = metadata.get('refactoring_type', 'Unknown')

            suggestions.append(f"\n### Pattern {i}: {refactoring_type}")

            # Truncate long content for readability
            if len(content) > 500:
                suggestions.append(content[:500] + "...")
            else:
                suggestions.append(content)

        return suggestions
