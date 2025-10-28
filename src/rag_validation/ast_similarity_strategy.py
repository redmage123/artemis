#!/usr/bin/env python3
"""
AST Similarity Strategy

WHY: Abstract Syntax Tree comparison is the most accurate way to detect logical
differences that text-based comparison misses. It catches hallucinations in
control flow, function calls, and variable usage patterns.

RESPONSIBILITY:
- Parse code into Abstract Syntax Trees
- Extract and compare AST node type features
- Handle syntax errors gracefully
- Generate AST-specific suggestions

PATTERNS:
- Strategy Pattern implementation
- AST visitor pattern for feature extraction
- Error handling with fallback results
- Helper methods to avoid nested loops
"""

import ast
from collections import defaultdict
from typing import Dict, List, Optional
from rag_validation.similarity_strategy import SimilarityStrategy
from rag_validation.rag_example import RAGExample
from rag_validation.similarity_result import SimilarityResult


class ASTSimilarityStrategy(SimilarityStrategy):
    """
    Computes similarity using Abstract Syntax Tree analysis.

    WHY: AST comparison catches logical differences that text comparison misses.
         Detects hallucinations in control flow, function calls, variable usage.

    WHAT: Parses code to AST and compares tree structures.
    PERFORMANCE: AST parsing is O(n), comparison is O(nodes).
    """

    def compute_similarity(
        self,
        generated_code: str,
        rag_example: RAGExample,
        context: Optional[Dict] = None
    ) -> SimilarityResult:
        """
        Compute AST-based similarity.

        WHY: Most accurate validation of code logic and structure.
        PERFORMANCE: Cached AST parsing, minimal tree walking.
        """
        try:
            # Parse to AST
            gen_ast = ast.parse(generated_code)
            rag_ast = ast.parse(rag_example.code)

            # Extract AST features
            gen_features = self._extract_ast_features(gen_ast)
            rag_features = self._extract_ast_features(rag_ast)

            # Compute similarity
            score = self._compute_ast_similarity(gen_features, rag_features)

            # Identify differences
            differences = self._identify_ast_differences(gen_features, rag_features)

            # Generate suggestions
            suggestions = self._generate_ast_suggestions(differences, rag_example)

            return SimilarityResult(
                score=score,
                strategy_name=self.get_strategy_name(),
                matched_example=rag_example,
                differences=differences,
                suggestions=suggestions
            )

        except SyntaxError as e:
            # If code doesn't parse, it's definitely not similar
            return SimilarityResult(
                score=0.0,
                strategy_name=self.get_strategy_name(),
                matched_example=rag_example,
                differences=[f"Syntax error: {e}"],
                suggestions=["Fix syntax errors before validation"]
            )

    def _extract_ast_features(self, tree: ast.AST) -> Dict[str, int]:
        """
        Extract features from AST.

        WHY: Convert AST to numeric features for comparison.
        PERFORMANCE: Single tree walk, O(nodes).
        """
        features = defaultdict(int)

        # Walk AST and count node types
        for node in ast.walk(tree):
            node_type = type(node).__name__
            features[node_type] += 1

        return dict(features)

    def _compute_ast_similarity(
        self,
        features1: Dict[str, int],
        features2: Dict[str, int]
    ) -> float:
        """
        Compute similarity from AST features.

        WHY: Quantify AST similarity for validation decision.
        PERFORMANCE: O(unique_node_types), typically small.
        """
        # Get all node types
        all_types = set(features1.keys()) | set(features2.keys())

        if not all_types:
            return 0.0

        # Compute similarity for each node type
        total_similarity = 0.0

        for node_type in all_types:
            count1 = features1.get(node_type, 0)
            count2 = features2.get(node_type, 0)

            max_count = max(count1, count2, 1)
            min_count = min(count1, count2)

            total_similarity += min_count / max_count

        # Average similarity across all node types
        return total_similarity / len(all_types)

    def _identify_ast_differences(
        self,
        gen_features: Dict[str, int],
        rag_features: Dict[str, int]
    ) -> List[str]:
        """Identify AST structural differences."""
        differences = []

        all_types = set(gen_features.keys()) | set(rag_features.keys())

        for node_type in all_types:
            gen_count = gen_features.get(node_type, 0)
            rag_count = rag_features.get(node_type, 0)

            # Significant difference threshold
            if abs(gen_count - rag_count) > 0:
                differences.append(
                    f"{node_type}: generated has {gen_count}, example has {rag_count}"
                )

        return differences

    def _generate_ast_suggestions(
        self,
        differences: List[str],
        rag_example: RAGExample
    ) -> List[str]:
        """
        Generate AST-based suggestions.

        WHY: Provide actionable feedback for AST differences.
        WHAT: Uses helper function to avoid nested for loops (anti-pattern).
        """
        # Map AST differences to actionable suggestions
        ast_to_suggestion = {
            'FunctionDef': 'Review function definitions',
            'ClassDef': 'Review class structure',
            'Call': 'Review function/method calls',
            'If': 'Review conditional logic',
            'For': 'Review loop structure',
            'Try': 'Review exception handling',
        }

        suggestions = []

        # Find matching suggestion for each difference (no nested loops)
        for diff in differences:
            matching_suggestion = self._find_matching_suggestion(
                diff, ast_to_suggestion, rag_example
            )
            if matching_suggestion:
                suggestions.append(matching_suggestion)

        return suggestions

    def _find_matching_suggestion(
        self,
        diff: str,
        ast_to_suggestion: Dict[str, str],
        rag_example: RAGExample
    ) -> Optional[str]:
        """
        Find matching suggestion for a difference.

        WHY: Helper method to avoid nested loops (extracts inner loop logic).
        PERFORMANCE: Early return when match found.
        """
        for node_type, suggestion in ast_to_suggestion.items():
            if node_type in diff:
                return f"{suggestion} from {rag_example.source}"

        return None

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "ASTSimilarity"
