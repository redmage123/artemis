#!/usr/bin/env python3
"""
Refactoring Suggestion Generator

WHY: Generate actionable refactoring suggestions based on review failures
RESPONSIBILITY: Create comprehensive refactoring guidance for developers
PATTERNS: Builder Pattern, Template Method, Single Responsibility
"""

from typing import Dict, List, Optional

from artemis_stage_interface import LoggerInterface
from rag_agent import RAGAgent


class RefactoringSuggestionGenerator:
    """
    Generate refactoring suggestions from code review failures.

    WHY: Separate refactoring suggestion logic from review execution
    RESPONSIBILITY: Build actionable refactoring guidance
    PATTERNS: Builder Pattern, Template Method
    """

    def __init__(self, rag: Optional[RAGAgent], logger: LoggerInterface):
        """
        Initialize refactoring generator.

        Args:
            rag: Optional RAG agent for knowledge-based suggestions
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

        WHY: Provide actionable guidance for fixing review failures
        RESPONSIBILITY: Orchestrate suggestion generation
        PATTERN: Template Method, Builder Pattern

        Args:
            review_results: List of review results
            card_id: Card identifier
            task_title: Task title

        Returns:
            Formatted refactoring suggestions text
        """
        self.logger.log("🔧 Generating refactoring suggestions based on code review failures...", "INFO")

        suggestions = []
        suggestions.extend(self._build_suggestion_header(task_title, card_id))
        suggestions.extend(self._build_developer_suggestions(review_results))
        suggestions.extend(self._build_general_best_practices())
        suggestions.extend(self._build_rag_suggestions())

        suggestion_text = "\n".join(suggestions)
        self.logger.log(f"✅ Generated {len(suggestions)} lines of refactoring suggestions", "INFO")

        return suggestion_text

    def _build_suggestion_header(self, task_title: str, card_id: str) -> List[str]:
        """
        Build header for refactoring suggestions.

        WHY: Consistent header format
        PATTERN: Builder Pattern
        """
        return [
            "# REFACTORING INSTRUCTIONS FOR CODE REVIEW FAILURES\n",
            f"**Task**: {task_title}",
            f"**Card ID**: {card_id}\n",
            "The following refactorings are required to pass code review:\n"
        ]

    def _build_developer_suggestions(self, review_results: List[Dict]) -> List[str]:
        """
        Build developer-specific refactoring suggestions.

        WHY: Provide targeted suggestions per developer
        RESPONSIBILITY: Extract and format developer issues
        PATTERN: Iterator Pattern, Guard Clause

        Args:
            review_results: List of review results

        Returns:
            List of suggestion lines
        """
        suggestions = []

        for result in review_results:
            developer_name = result.get('developer_name', 'unknown')
            review_status = result.get('review_status', 'UNKNOWN')

            # Skip passing reviews
            if review_status not in ["FAIL", "NEEDS_IMPROVEMENT"]:
                continue

            critical_issues = result.get('critical_issues', 0)
            high_issues = result.get('high_issues', 0)

            suggestions.extend([
                f"\n## {developer_name} - Refactoring Required",
                f"Status: {review_status}",
                f"Critical Issues: {critical_issues}",
                f"High Issues: {high_issues}\n"
            ])

            suggestions.extend(self._get_standard_refactoring_recommendations())

        return suggestions

    def _get_standard_refactoring_recommendations(self) -> List[str]:
        """
        Get standard refactoring recommendations list.

        WHY: Reusable standard recommendations
        PATTERN: Template Method
        """
        return [
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

    def _build_general_best_practices(self) -> List[str]:
        """
        Build general best practices section.

        WHY: Provide general guidance beyond specific issues
        PATTERN: Template Method
        """
        return [
            "\n## General Best Practices",
            "- Follow language-specific idioms and conventions",
            "- Keep methods focused on a single responsibility",
            "- Prefer composition over inheritance",
            "- Use dependency injection for better testability",
            "- Write self-documenting code",
            "- Add unit tests for all refactored code",
            "- Ensure all tests pass after refactoring\n"
        ]

    def _build_rag_suggestions(self) -> List[str]:
        """
        Query RAG for additional refactoring patterns.

        WHY: Leverage historical knowledge for better suggestions
        RESPONSIBILITY: Query and format RAG results
        PATTERN: Guard Clause, Early Return

        Returns:
            List of RAG-based suggestion lines
        """
        if not self.rag:
            return []

        try:
            rag_suggestions = self.rag.query_similar(
                query_text="refactoring patterns code quality best practices",
                artifact_type="architecture_decision",
                top_k=3
            )

            if not rag_suggestions:
                return []

            return self._format_rag_suggestions(rag_suggestions)

        except Exception as e:
            self.logger.log(f"Could not query RAG for additional patterns: {e}", "WARNING")
            return []

    def _format_rag_suggestions(self, rag_suggestions: List[Dict]) -> List[str]:
        """
        Format RAG suggestions into readable text.

        WHY: Separate formatting logic
        PATTERN: Formatter Pattern, Iterator
        """
        suggestions = ["\n## Additional Refactoring Patterns from Knowledge Base"]

        for i, result in enumerate(rag_suggestions, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            refactoring_type = metadata.get('refactoring_type', 'Unknown')

            suggestions.append(f"\n### Pattern {i}: {refactoring_type}")

            # Truncate long content
            if len(content) > 500:
                suggestions.append(content[:500] + "...")
            else:
                suggestions.append(content)

        return suggestions


class RefactoringRecommendations:
    """
    Standard refactoring recommendations catalog.

    WHY: Centralized catalog of refactoring patterns
    RESPONSIBILITY: Provide categorized refactoring recommendations
    PATTERNS: Catalog Pattern, Factory Pattern
    """

    @staticmethod
    def get_by_category(category: str) -> List[str]:
        """
        Get refactoring recommendations by category.

        WHY: Enable category-specific suggestions
        PATTERN: Factory Pattern, Dispatch Table

        Args:
            category: Category name (security, quality, performance, etc.)

        Returns:
            List of recommendations for category
        """
        catalog = {
            'security': RefactoringRecommendations._security_recommendations(),
            'quality': RefactoringRecommendations._quality_recommendations(),
            'performance': RefactoringRecommendations._performance_recommendations(),
            'maintainability': RefactoringRecommendations._maintainability_recommendations(),
        }

        return catalog.get(category, [])

    @staticmethod
    def _security_recommendations() -> List[str]:
        """Security-focused refactoring recommendations."""
        return [
            "- Validate and sanitize all user inputs",
            "- Use parameterized queries to prevent SQL injection",
            "- Implement proper authentication and authorization",
            "- Encrypt sensitive data at rest and in transit",
            "- Apply principle of least privilege",
            "- Handle errors without exposing sensitive information"
        ]

    @staticmethod
    def _quality_recommendations() -> List[str]:
        """Code quality refactoring recommendations."""
        return [
            "- Extract methods to reduce complexity",
            "- Apply DRY principle to eliminate duplication",
            "- Use meaningful variable and method names",
            "- Add comprehensive error handling",
            "- Write unit tests for all public methods",
            "- Add type hints for better IDE support"
        ]

    @staticmethod
    def _performance_recommendations() -> List[str]:
        """Performance refactoring recommendations."""
        return [
            "- Cache frequently accessed data",
            "- Use lazy loading for expensive operations",
            "- Optimize database queries (use indexes, avoid N+1)",
            "- Process large datasets in batches",
            "- Use async/await for I/O operations",
            "- Profile code to identify bottlenecks"
        ]

    @staticmethod
    def _maintainability_recommendations() -> List[str]:
        """Maintainability refactoring recommendations."""
        return [
            "- Keep methods under 50 lines",
            "- Limit cyclomatic complexity to 10 or less",
            "- Use dependency injection",
            "- Follow SOLID principles",
            "- Write self-documenting code",
            "- Add comprehensive documentation"
        ]
