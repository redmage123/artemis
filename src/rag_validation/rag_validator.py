#!/usr/bin/env python3
"""
RAG Validator

WHY: Main orchestrator that combines multiple similarity strategies to validate
generated code against RAG-retrieved examples. Reduces hallucinations by ensuring
code follows proven patterns from authoritative sources.

RESPONSIBILITY:
- Query RAG database for similar code examples
- Apply multiple similarity strategies (structural, semantic, AST)
- Aggregate strategy results into final validation decision
- Generate comprehensive feedback with warnings and recommendations
- Manage caching for performance

PATTERNS:
- Chain of Responsibility: Multiple strategies applied sequentially
- Strategy Pattern: Pluggable similarity algorithms
- Cache Pattern: Performance optimization
- Guard clauses to avoid nested conditionals
"""

import hashlib
from typing import Dict, List, Optional
from rag_validation.rag_example import RAGExample
from rag_validation.validation_result import RAGValidationResult
from rag_validation.similarity_result import SimilarityResult
from rag_validation.similarity_strategy import SimilarityStrategy
from rag_validation.query_cache import RAGQueryCache
from rag_validation.structural_similarity_strategy import StructuralSimilarityStrategy
from rag_validation.semantic_similarity_strategy import SemanticSimilarityStrategy
from rag_validation.ast_similarity_strategy import ASTSimilarityStrategy


class RAGValidator:
    """
    Main RAG-enhanced validator using multiple strategies.

    WHY: Combines multiple similarity strategies for robust validation.
         Each strategy catches different types of hallucinations.

    WHAT: Queries RAG, applies strategies, aggregates results.
    ARCHITECTURE: Chain of Responsibility for strategies.
    """

    def __init__(
        self,
        rag_agent,
        strategies: Optional[List[SimilarityStrategy]] = None,
        cache: Optional[RAGQueryCache] = None,
        min_similarity_threshold: float = 0.3,
        min_confidence_threshold: float = 0.6
    ):
        """
        Initialize RAG validator with strategies and thresholds.

        Args:
            rag_agent: RAG agent for querying code examples
            strategies: List of similarity strategies to use
            cache: Query cache (creates default if None)
            min_similarity_threshold: Minimum similarity to pass
            min_confidence_threshold: Minimum confidence to pass
        """
        self.rag = rag_agent
        self.cache = cache or RAGQueryCache()
        self.min_similarity = min_similarity_threshold
        self.min_confidence = min_confidence_threshold

        # Initialize strategies (default: all three)
        self.strategies = strategies or [
            StructuralSimilarityStrategy(),
            SemanticSimilarityStrategy(),
            ASTSimilarityStrategy(),
        ]

    def validate_code(
        self,
        generated_code: str,
        context: Optional[Dict] = None,
        top_k: int = 5
    ) -> RAGValidationResult:
        """
        Validate generated code against RAG examples.

        WHY: Main validation entry point. Orchestrates RAG query,
             strategy execution, and result aggregation.

        WHAT:
        1. Query RAG for similar code patterns
        2. Apply all similarity strategies
        3. Aggregate results and make decision
        4. Generate actionable feedback

        Args:
            generated_code: Code to validate
            context: Language, framework, requirements
            top_k: Number of RAG examples to retrieve

        Returns:
            RAGValidationResult with pass/fail and detailed feedback
        """
        context = context or {}

        # Step 1: Query RAG for similar examples (with caching)
        similar_examples = self._query_rag_with_cache(
            generated_code, context, top_k
        )

        # Step 2: No similar examples found - potential hallucination
        if not similar_examples:
            return self._create_no_examples_result()

        # Step 3: Apply all strategies to each example
        all_similarity_results = self._apply_strategies(
            generated_code, similar_examples, context
        )

        # Step 4: Aggregate results and make decision
        validation_result = self._aggregate_results(
            similar_examples, all_similarity_results
        )

        return validation_result

    def _query_rag_with_cache(
        self,
        code: str,
        context: Dict,
        top_k: int
    ) -> List[RAGExample]:
        """
        Query RAG with caching for performance.

        WHY: RAG queries are expensive, cache prevents redundant queries.
        PERFORMANCE: O(1) cache hit, O(n) cache miss (RAG query).
        """
        # Create cache key from code and context
        cache_key = self._create_cache_key(code, context)

        # Check cache first
        cached_examples = self.cache.get(cache_key)

        if cached_examples is not None:
            return cached_examples

        # Cache miss - query RAG
        examples = self._query_rag(code, context, top_k)

        # Store in cache
        self.cache.put(cache_key, examples)

        return examples

    def _create_cache_key(self, code: str, context: Dict) -> str:
        """
        Create cache key from code and context.

        WHY: Unique key for cache lookup.
        PERFORMANCE: O(n) hash computation.
        """
        # Hash code content
        code_hash = hashlib.md5(code.encode()).hexdigest()

        # Include context in key
        context_parts = [
            context.get('language', 'unknown'),
            context.get('framework', 'none'),
        ]

        cache_key = f"{code_hash}:{':'.join(context_parts)}"

        return cache_key

    def _query_rag(
        self,
        code: str,
        context: Dict,
        top_k: int
    ) -> List[RAGExample]:
        """
        Query RAG database for similar code examples.

        WHY: Retrieve proven code patterns for comparison.
        PERFORMANCE: Depends on RAG implementation (vector search).
        """
        try:
            # Query RAG for code examples
            results = self.rag.search_code_examples(
                query=code,
                language=context.get('language'),
                framework=context.get('framework'),
                top_k=top_k
            )

            # Convert to RAGExample objects
            examples = []

            for result in results:
                example = RAGExample(
                    code=result.get('code', ''),
                    source=result.get('source', 'unknown'),
                    language=result.get('language', context.get('language', 'python')),
                    framework=result.get('framework'),
                    metadata=result.get('metadata', {}),
                    relevance_score=result.get('score', 0.0)
                )
                examples.append(example)

            return examples

        except Exception as e:
            # Log error but don't fail validation
            # Return empty list - validation will handle this case
            return []

    def _apply_strategies(
        self,
        generated_code: str,
        examples: List[RAGExample],
        context: Dict
    ) -> List[SimilarityResult]:
        """
        Apply all strategies to all examples.

        WHY: Multiple strategies catch different hallucination types.
        PERFORMANCE: O(strategies * examples), parallelizable.
        """
        all_results = []

        # Apply each strategy to each example
        for strategy in self.strategies:
            for example in examples:
                result = strategy.compute_similarity(
                    generated_code, example, context
                )
                all_results.append(result)

        return all_results

    def _aggregate_results(
        self,
        examples: List[RAGExample],
        similarity_results: List[SimilarityResult]
    ) -> RAGValidationResult:
        """
        Aggregate similarity results into final validation decision.

        WHY: Combine multiple strategy results for robust decision.
        WHAT: Uses weighted voting across strategies.
        """
        # Calculate average similarity across all strategies
        avg_similarity = sum(r.score for r in similarity_results) / max(1, len(similarity_results))

        # Calculate confidence based on result consistency
        confidence = self._calculate_confidence(similarity_results)

        # Validation passes if similarity and confidence meet thresholds
        passed = (
            avg_similarity >= self.min_similarity and
            confidence >= self.min_confidence
        )

        # Collect warnings and recommendations
        warnings = self._collect_warnings(similarity_results, avg_similarity)
        recommendations = self._collect_recommendations(similarity_results, examples)

        return RAGValidationResult(
            passed=passed,
            confidence=confidence,
            similar_examples=examples,
            similarity_results=similarity_results,
            warnings=warnings,
            recommendations=recommendations
        )

    def _calculate_confidence(self, results: List[SimilarityResult]) -> float:
        """
        Calculate confidence based on result consistency.

        WHY: High confidence if strategies agree, low if they disagree.
        """
        if not results:
            return 0.0

        scores = [r.score for r in results]

        # Confidence is inverse of score variance
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)

        # Normalize confidence to 0-1 range
        confidence = 1.0 / (1.0 + variance)

        return confidence

    def _collect_warnings(
        self,
        results: List[SimilarityResult],
        avg_similarity: float
    ) -> List[str]:
        """Collect warnings from similarity results."""
        warnings = []

        # Low similarity warning
        if avg_similarity < self.min_similarity:
            warnings.append(
                f"Code similarity ({avg_similarity:.2f}) below threshold "
                f"({self.min_similarity:.2f})"
            )

        # Collect unique differences
        unique_diffs = set()
        for result in results:
            unique_diffs.update(result.differences)

        warnings.extend(unique_diffs)

        return list(warnings)

    def _collect_recommendations(
        self,
        results: List[SimilarityResult],
        examples: List[RAGExample]
    ) -> List[str]:
        """Collect recommendations from similarity results."""
        recommendations = []

        # Collect unique suggestions
        unique_suggestions = set()
        for result in results:
            unique_suggestions.update(result.suggestions)

        recommendations.extend(unique_suggestions)

        # Add references to similar examples
        if examples:
            best_example = max(examples, key=lambda e: e.relevance_score)
            recommendations.append(
                f"Review similar implementation in {best_example.source}"
            )

        return list(recommendations)

    def _create_no_examples_result(self) -> RAGValidationResult:
        """
        Create result when no RAG examples found.

        WHY: No examples might indicate hallucinated approach.
        """
        return RAGValidationResult(
            passed=False,
            confidence=0.0,
            similar_examples=[],
            similarity_results=[],
            warnings=[
                "No similar code patterns found in RAG database",
                "Generated code may use unusual or hallucinated approach"
            ],
            recommendations=[
                "Review code carefully - pattern not found in proven sources",
                "Consider using more common approach with proven examples"
            ]
        )
