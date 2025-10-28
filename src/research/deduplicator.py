#!/usr/bin/env python3
"""
WHY: Remove duplicate examples
RESPONSIBILITY: Deduplicate based on content similarity
PATTERNS: Strategy (deduplication algorithm)

Deduplicator uses hash-based approach for performance.
"""

from typing import List
from research_strategy import ResearchExample


class ExampleDeduplicator:
    """
    Removes duplicate examples based on content similarity.

    WHY: Deduplication improves quality and reduces storage.
    RESPONSIBILITY: Identify and remove duplicate content.
    PATTERNS: Strategy (hash-based deduplication).
    """

    @staticmethod
    def deduplicate(examples: List[ResearchExample]) -> List[ResearchExample]:
        """
        Remove duplicate examples based on content similarity.

        WHY: Uses simple hash-based deduplication for O(n) performance.

        Args:
            examples: List of research examples

        Returns:
            Deduplicated list

        Example:
            >>> examples = [example1, example2, example1]  # duplicate
            >>> unique = ExampleDeduplicator.deduplicate(examples)
            >>> len(unique)
            2
        """
        # Guard clause - empty list
        if not examples:
            return []

        # Use set for O(1) lookup instead of O(n) list contains
        seen_hashes = set()
        unique_examples = []

        for example in examples:
            # Create simple content hash (first 1000 chars for performance)
            content_hash = hash(example.content[:1000])

            # Guard clause - skip if seen
            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)
            unique_examples.append(example)

        return unique_examples
