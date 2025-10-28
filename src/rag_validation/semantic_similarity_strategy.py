#!/usr/bin/env python3
"""
Semantic Similarity Strategy

WHY: Code can be structurally different but semantically similar. This strategy
catches hallucinations where the implementation approach differs from proven
patterns, even when the structure might look reasonable.

RESPONSIBILITY:
- Tokenize code for semantic-level comparison
- Compute sequence similarity using difflib
- Identify semantic differences and generate suggestions
- Handle code normalization (removing comments, whitespace)

PATTERNS:
- Strategy Pattern implementation
- Token-based comparison for robustness
- Guard clauses for early returns
"""

import re
import difflib
from typing import Dict, List, Optional, Tuple
from rag_validation.similarity_strategy import SimilarityStrategy
from rag_validation.rag_example import RAGExample
from rag_validation.similarity_result import SimilarityResult


class SemanticSimilarityStrategy(SimilarityStrategy):
    """
    Computes semantic similarity using token-based comparison.

    WHY: Code can be structurally different but semantically similar.
         This catches hallucinations where implementation differs
         from proven approaches.

    WHAT: Uses difflib and token sequence matching for semantic comparison.
    PERFORMANCE: Optimized with sequence matcher for O(n*m) comparison.
    """

    def compute_similarity(
        self,
        generated_code: str,
        rag_example: RAGExample,
        context: Optional[Dict] = None
    ) -> SimilarityResult:
        """
        Compute semantic similarity using sequence matching.

        WHY: Catches cases where code looks different but does same thing.
        PERFORMANCE: Uses difflib's optimized C implementation.
        """
        # Tokenize code for semantic comparison
        gen_tokens = self._tokenize_code(generated_code)
        rag_tokens = self._tokenize_code(rag_example.code)

        # Compute sequence similarity
        matcher = difflib.SequenceMatcher(None, gen_tokens, rag_tokens)
        score = matcher.ratio()

        # Get matching blocks
        matches = matcher.get_matching_blocks()

        # Identify semantic differences
        differences = self._identify_semantic_differences(
            generated_code, rag_example.code, matches
        )

        # Generate suggestions
        suggestions = self._generate_semantic_suggestions(differences, rag_example)

        return SimilarityResult(
            score=score,
            strategy_name=self.get_strategy_name(),
            matched_example=rag_example,
            differences=differences,
            suggestions=suggestions
        )

    def _tokenize_code(self, code: str) -> List[str]:
        """
        Tokenize code for semantic comparison.

        WHY: Token-level comparison is more robust than character-level.
        PERFORMANCE: Simple regex split, O(n).
        """
        # Remove comments and whitespace for cleaner comparison
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        code = re.sub(r"'''[\s\S]*?'''", '', code)

        # Tokenize on word boundaries and operators
        tokens = re.findall(r'\w+|[^\w\s]', code)

        return tokens

    def _identify_semantic_differences(
        self,
        gen_code: str,
        rag_code: str,
        matches: List[Tuple[int, int, int]]
    ) -> List[str]:
        """
        Identify semantic differences using matching blocks.

        WHY: Highlight what's semantically different for feedback.
        """
        differences = []

        # If overall similarity is low, provide general feedback
        total_matched = sum(match[2] for match in matches)
        gen_lines = gen_code.split('\n')

        if total_matched < len(gen_code) * 0.5:
            differences.append(
                "Generated code semantically differs from proven patterns"
            )

        return differences

    def _generate_semantic_suggestions(
        self,
        differences: List[str],
        rag_example: RAGExample
    ) -> List[str]:
        """Generate suggestions for semantic improvements."""
        suggestions = []

        if differences:
            suggestions.append(
                f"Review approach used in {rag_example.source} "
                f"({rag_example.language})"
            )

        return suggestions

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "SemanticSimilarity"
