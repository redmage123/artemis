#!/usr/bin/env python3
"""
WHY: Format research results into human-readable summaries
RESPONSIBILITY: Create structured summaries of research findings
PATTERNS: Formatter (presentation logic), Guard Clauses

Summary formatter converts raw research data into readable summaries showing
source distribution, example counts, and top results.
"""

from typing import List, Dict
from research_strategy import ResearchExample, ResearchStrategy


class SummaryFormatter:
    """
    Formats research results into summaries.

    WHY: Developers need clear overview of what examples were found and where.
    PATTERNS: Pure function (stateless formatting), Guard clauses.
    """

    def format_summary(
        self,
        examples: List[ResearchExample],
        strategies: List[ResearchStrategy]
    ) -> str:
        """
        Build research summary.

        WHY: Provides overview of research results for visibility and debugging.

        Args:
            examples: Examples found
            strategies: Strategies used

        Returns:
            Summary string

        Example:
            Found 15 code examples from 3 sources:
              - GitHub: 8 examples
              - HuggingFace: 5 examples
              - local: 2 examples

            Top examples:
              - JWT Authentication (GitHub, score: 0.95)
              - Flask Auth Tutorial (HuggingFace, score: 0.87)
        """
        # Guard clause - early return for empty results
        if not examples:
            return "No examples found"

        return self._build_summary_content(examples, strategies)

    def _build_summary_content(
        self,
        examples: List[ResearchExample],
        strategies: List[ResearchStrategy]
    ) -> str:
        """
        Build the summary content.

        WHY: Separation allows guard clause to avoid unnecessary processing.

        Args:
            examples: Examples found (guaranteed non-empty by caller)
            strategies: Strategies used

        Returns:
            Formatted summary string
        """
        # Count examples by source
        source_counts = self._count_by_source(examples)

        # Build summary lines using comprehension
        summary_lines = [
            f"Found {len(examples)} code examples from {len(strategies)} sources:",
            *[f"  - {source}: {count} examples"
              for source, count in source_counts.items()],
            f"\nTop examples:",
            *[f"  - {example.title} ({example.source}, score: {example.relevance_score:.2f})"
              for example in examples[:5]]
        ]

        return "\n".join(summary_lines)

    def _count_by_source(self, examples: List[ResearchExample]) -> Dict[str, int]:
        """
        Count examples by source.

        WHY: Shows distribution of results across sources.

        Args:
            examples: Examples to count

        Returns:
            Dictionary mapping source name to count
        """
        source_counts = {}
        for example in examples:
            source_counts[example.source] = source_counts.get(example.source, 0) + 1

        return source_counts
