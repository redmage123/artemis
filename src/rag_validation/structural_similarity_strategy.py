#!/usr/bin/env python3
"""
Structural Similarity Strategy

WHY: Computes code similarity based on structural patterns (indentation, blocks,
patterns) to catch hallucinations where code structure differs from proven patterns.
This is the fastest similarity check and serves as a first-pass filter.

RESPONSIBILITY:
- Extract structural features from code (functions, classes, imports, etc.)
- Compute similarity scores based on structural metrics
- Identify structural differences and generate suggestions
- Cache extracted features for performance

PATTERNS:
- Strategy Pattern implementation
- Feature extraction with caching
- Guard clauses to avoid nested conditionals
- Dictionary-based dispatch instead of if/elif chains
"""

import re
import hashlib
from typing import Dict, List, Optional
from rag_validation.similarity_strategy import SimilarityStrategy
from rag_validation.rag_example import RAGExample
from rag_validation.similarity_result import SimilarityResult


class StructuralSimilarityStrategy(SimilarityStrategy):
    """
    Computes similarity based on code structure (indentation, blocks, patterns).

    WHY: Structural similarity catches hallucinations where code structure
         differs from proven patterns (e.g., using wrong indentation style,
         incorrect control flow structure).

    WHAT: Analyzes code structure using regex patterns and string metrics.
    PERFORMANCE: Uses compiled regex patterns for fast matching.
    """

    # Compile regex patterns once for performance
    _PATTERNS = {
        'function_def': re.compile(r'def\s+\w+\s*\([^)]*\)\s*:', re.MULTILINE),
        'class_def': re.compile(r'class\s+\w+\s*(?:\([^)]*\))?\s*:', re.MULTILINE),
        'import_stmt': re.compile(r'^(?:from\s+\S+\s+)?import\s+.+$', re.MULTILINE),
        'decorator': re.compile(r'@\w+(?:\([^)]*\))?', re.MULTILINE),
        'docstring': re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', re.MULTILINE),
    }

    def __init__(self):
        """Initialize strategy with performance optimizations."""
        self._cache = {}  # Cache structural features for performance

    def compute_similarity(
        self,
        generated_code: str,
        rag_example: RAGExample,
        context: Optional[Dict] = None
    ) -> SimilarityResult:
        """
        Compute structural similarity using pattern matching.

        WHY: Fast initial check for structural correctness before
             expensive semantic analysis.

        PERFORMANCE: O(n) where n is code length, uses cached features.
        """
        # Extract structural features (cached for performance)
        gen_features = self._extract_features(generated_code)
        rag_features = self._extract_features(rag_example.code)

        # Compute feature similarity
        score = self._compute_feature_similarity(gen_features, rag_features)

        # Identify differences
        differences = self._identify_differences(gen_features, rag_features)

        # Generate suggestions
        suggestions = self._generate_suggestions(differences, rag_example)

        return SimilarityResult(
            score=score,
            strategy_name=self.get_strategy_name(),
            matched_example=rag_example,
            differences=differences,
            suggestions=suggestions
        )

    def _extract_features(self, code: str) -> Dict[str, int]:
        """
        Extract structural features from code.

        WHY: Convert code to numeric features for fast comparison.
        PERFORMANCE: Results are cached using code hash.
        """
        # Cache lookup for performance
        code_hash = hashlib.md5(code.encode()).hexdigest()

        if code_hash in self._cache:
            return self._cache[code_hash]

        features = {
            'function_count': len(self._PATTERNS['function_def'].findall(code)),
            'class_count': len(self._PATTERNS['class_def'].findall(code)),
            'import_count': len(self._PATTERNS['import_stmt'].findall(code)),
            'decorator_count': len(self._PATTERNS['decorator'].findall(code)),
            'docstring_count': len(self._PATTERNS['docstring'].findall(code)),
            'line_count': len(code.split('\n')),
            'avg_line_length': sum(len(line) for line in code.split('\n')) / max(1, len(code.split('\n'))),
        }

        # Cache for future use
        self._cache[code_hash] = features

        return features

    def _compute_feature_similarity(
        self,
        features1: Dict[str, int],
        features2: Dict[str, int]
    ) -> float:
        """
        Compute similarity score from features.

        WHY: Normalize feature differences to 0-1 similarity score.
        PERFORMANCE: O(1) - fixed number of features.
        """
        # Use weighted features (some are more important)
        weights = {
            'function_count': 0.2,
            'class_count': 0.2,
            'import_count': 0.15,
            'decorator_count': 0.1,
            'docstring_count': 0.1,
            'line_count': 0.15,
            'avg_line_length': 0.1,
        }

        total_score = 0.0

        for feature, weight in weights.items():
            val1 = features1.get(feature, 0)
            val2 = features2.get(feature, 0)

            # Avoid division by zero
            max_val = max(val1, val2, 1)
            min_val = min(val1, val2)

            # Feature similarity: 1.0 if identical, lower if different
            feature_similarity = min_val / max_val
            total_score += feature_similarity * weight

        return total_score

    def _identify_differences(
        self,
        gen_features: Dict[str, int],
        rag_features: Dict[str, int]
    ) -> List[str]:
        """
        Identify structural differences between code samples.

        WHY: Provide actionable feedback on what's different.
        """
        differences = []

        # Check each feature for significant differences
        for feature, gen_val in gen_features.items():
            rag_val = rag_features.get(feature, 0)

            # Significant difference threshold
            if abs(gen_val - rag_val) / max(gen_val, rag_val, 1) > 0.3:
                differences.append(
                    f"{feature}: generated has {gen_val}, example has {rag_val}"
                )

        return differences

    def _generate_suggestions(
        self,
        differences: List[str],
        rag_example: RAGExample
    ) -> List[str]:
        """
        Generate actionable suggestions based on differences.

        WHY: Help developers fix hallucinations with specific guidance.
        WHAT: Uses dictionary mapping instead of if/elif chain (avoids anti-pattern).
        """
        # Map difference types to suggestion templates (avoid if/elif chain)
        diff_to_suggestion = {
            'function_count': f"Consider splitting into functions like in {rag_example.source}",
            'class_count': f"Review class structure from {rag_example.source}",
            'docstring_count': "Add docstrings to match documentation standards",
        }

        suggestions = []

        # Generate suggestions using dictionary lookup (no nested ifs)
        for diff in differences:
            suggestion = next(
                (template for key, template in diff_to_suggestion.items() if key in diff),
                None
            )
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "StructuralSimilarity"
