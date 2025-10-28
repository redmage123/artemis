#!/usr/bin/env python3
"""
WHY: Rank examples by relevance
RESPONSIBILITY: Calculate relevance scores with boost factors
PATTERNS: Strategy (ranking algorithm), Dispatch Table (source priority)

Ranker improves search results with query/technology matching.
"""

from typing import List
from research.models import ResearchExample


class ExampleRanker:
    """
    Ranks examples by relevance to query and technologies.

    WHY: Relevance ranking improves search result quality.
    RESPONSIBILITY: Calculate boosted scores based on multiple factors.
    PATTERNS: Strategy (ranking algorithm), Dispatch table (source priority).
    """

    # Dispatch table: source → boost factor
    SOURCE_BOOST = {
        "github": 1.3,
        "huggingface": 1.2,
        "local": 1.0
    }

    @staticmethod
    def rank_by_relevance(
        examples: List[ResearchExample],
        query: str,
        technologies: List[str]
    ) -> List[ResearchExample]:
        """
        Rank examples by relevance to query and technologies.

        WHY: Boosted scoring helps prioritize best matches.

        Args:
            examples: List of examples to rank
            query: Search query
            technologies: Technologies list

        Returns:
            Sorted list by relevance score (highest first)

        Example:
            >>> ranked = ExampleRanker.rank_by_relevance(examples, "auth", ["python"])
            >>> ranked[0].relevance_score > ranked[1].relevance_score
            True
        """
        # Guard clause - empty list
        if not examples:
            return []

        # Prepare lowercase versions for matching
        query_lower = query.lower()
        tech_lower = [t.lower() for t in technologies]

        # Calculate boosted scores
        boosted_examples = []
        for example in examples:
            boost = ExampleRanker._calculate_boost(example, query_lower, tech_lower)
            boosted_score = example.relevance_score * boost

            # Create new example with boosted score
            boosted_example = ResearchExample(
                title=example.title,
                content=example.content,
                source=example.source,
                url=example.url,
                language=example.language,
                tags=example.tags,
                relevance_score=boosted_score
            )
            boosted_examples.append(boosted_example)

        # Sort by boosted score (descending)
        boosted_examples.sort(key=lambda x: x.relevance_score, reverse=True)

        return boosted_examples

    @staticmethod
    def _calculate_boost(
        example: ResearchExample,
        query: str,
        technologies: List[str]
    ) -> float:
        """
        Calculate relevance boost factor.

        WHY: Multiple factors contribute to relevance (title, tech, source).

        Args:
            example: Research example
            query: Query string (lowercase)
            technologies: Technologies list (lowercase)

        Returns:
            Boost factor (1.0 = no boost, >1.0 = boosted)
        """
        boost = 1.0

        # Boost for title match
        if query in example.title.lower():
            boost *= 1.5

        # Boost for technology match
        tech_matches = sum(
            1 for tech in technologies
            if tech in example.language.lower() or tech in " ".join(example.tags).lower()
        )
        boost *= (1.0 + tech_matches * 0.2)

        # Boost for source priority (dispatch table - no if/elif)
        boost *= ExampleRanker.SOURCE_BOOST.get(example.source.lower(), 1.0)

        return boost
