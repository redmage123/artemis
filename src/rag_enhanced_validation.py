#!/usr/bin/env python3
"""
RAG-Enhanced Validation System

WHY: LLMs hallucinate by generating code that doesn't match real-world patterns.
This module validates generated code against the RAG database of proven examples,
significantly reducing hallucinations by ensuring generated code follows patterns
that exist in authoritative sources (books, documentation, real codebases).

WHAT: Provides multi-strategy validation that:
1. Queries RAG for similar code patterns
2. Computes similarity using multiple strategies (structural, semantic, AST)
3. Validates generated code against proven patterns
4. Provides detailed feedback with references to similar examples

ARCHITECTURE:
- Strategy Pattern: Different similarity computation algorithms
- Factory Pattern: Create validators based on language/framework
- Chain of Responsibility: Multiple validation strategies
- Observer Pattern: Integration with pipeline_observer for real-time events
- SOLID Principles: Each class has single responsibility
"""

import ast
import re
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from functools import lru_cache
import difflib


@dataclass
class RAGExample:
    """
    Represents a code example retrieved from RAG database.

    WHY: Encapsulates RAG query results with metadata for similarity comparison.
    """
    code: str
    source: str  # Book, repo, documentation
    language: str
    framework: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0


@dataclass
class SimilarityResult:
    """
    Result of similarity comparison between generated code and RAG example.

    WHY: Provides detailed similarity metrics for validation decisions.
    """
    score: float  # 0.0 to 1.0
    strategy_name: str
    matched_example: RAGExample
    differences: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RAGValidationResult:
    """
    Complete validation result with all similarity comparisons.

    WHY: Aggregates results from multiple strategies for final decision.
    """
    passed: bool
    confidence: float  # 0.0 to 1.0
    similar_examples: List[RAGExample]
    similarity_results: List[SimilarityResult]
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)


class SimilarityStrategy(ABC):
    """
    Abstract base class for similarity computation strategies.

    WHY: Strategy Pattern allows different similarity algorithms
         without modifying validation logic. Each language/framework
         may require different similarity metrics.

    WHAT: Defines interface for computing similarity between
          generated code and RAG examples.
    """

    @abstractmethod
    def compute_similarity(
        self,
        generated_code: str,
        rag_example: RAGExample,
        context: Optional[Dict] = None
    ) -> SimilarityResult:
        """
        Compute similarity between generated code and RAG example.

        WHY: Abstract method ensures all strategies implement consistent interface.

        Args:
            generated_code: Code to validate
            rag_example: Reference code from RAG
            context: Additional context (language, framework, requirements)

        Returns:
            SimilarityResult with score and details
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy name for logging and debugging."""
        pass


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


class RAGQueryCache:
    """
    Caches RAG query results for performance.

    WHY: RAG queries are expensive (embedding computation, vector search).
         Caching prevents redundant queries for similar code.

    WHAT: LRU cache with TTL for RAG query results.
    PERFORMANCE: O(1) lookup, automatic eviction.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache with size and TTL limits.

        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time-to-live for cache entries
        """
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self._cache: Dict[str, Tuple[List[RAGExample], datetime]] = {}

    def get(self, cache_key: str) -> Optional[List[RAGExample]]:
        """
        Retrieve cached RAG results.

        WHY: Avoid expensive RAG queries for repeated validations.
        PERFORMANCE: O(1) dictionary lookup.
        """
        if cache_key not in self._cache:
            return None

        examples, timestamp = self._cache[cache_key]

        # Check if cache entry expired
        if datetime.now() - timestamp > self.ttl:
            del self._cache[cache_key]
            return None

        return examples

    def put(self, cache_key: str, examples: List[RAGExample]) -> None:
        """
        Store RAG results in cache.

        WHY: Cache for future validations of similar code.
        PERFORMANCE: O(1) insertion, O(n) eviction if cache full.
        """
        # Evict oldest entries if cache full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()

        self._cache[cache_key] = (examples, datetime.now())

    def _evict_oldest(self) -> None:
        """
        Evict oldest cache entries.

        WHY: Maintain cache size limit for memory efficiency.
        PERFORMANCE: O(n) to find oldest, could optimize with heap.
        """
        # Find oldest entry
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k][1]
        )

        del self._cache[oldest_key]

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()


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


class RAGValidationFactory:
    """
    Factory for creating RAG validators with framework-specific configurations.

    WHY: Different frameworks need different validation strategies and thresholds.
    WHAT: Factory Pattern for creating pre-configured validators.
    """

    # Framework-specific configurations
    _FRAMEWORK_CONFIGS = {
        'django': {
            'min_similarity': 0.4,
            'min_confidence': 0.7,
            'strategies': ['structural', 'semantic', 'ast']
        },
        'flask': {
            'min_similarity': 0.3,
            'min_confidence': 0.6,
            'strategies': ['structural', 'semantic', 'ast']
        },
        'rails': {
            'min_similarity': 0.4,
            'min_confidence': 0.7,
            'strategies': ['structural', 'semantic']  # No AST for Ruby
        },
        'react': {
            'min_similarity': 0.3,
            'min_confidence': 0.6,
            'strategies': ['structural', 'semantic']
        },
    }

    @staticmethod
    def create_validator(
        rag_agent,
        framework: Optional[str] = None,
        custom_config: Optional[Dict] = None
    ) -> RAGValidator:
        """
        Create validator with framework-specific configuration.

        WHY: Different frameworks have different validation requirements.

        Args:
            rag_agent: RAG agent instance
            framework: Framework name (django, flask, rails, etc.)
            custom_config: Override default configuration

        Returns:
            Configured RAGValidator instance
        """
        # Get framework config or use defaults
        config = RAGValidationFactory._FRAMEWORK_CONFIGS.get(
            framework.lower() if framework else 'default',
            {
                'min_similarity': 0.3,
                'min_confidence': 0.6,
                'strategies': ['structural', 'semantic', 'ast']
            }
        )

        # Apply custom config overrides
        if custom_config:
            config.update(custom_config)

        # Create strategies based on config
        strategies = RAGValidationFactory._create_strategies(
            config['strategies']
        )

        # Create validator
        return RAGValidator(
            rag_agent=rag_agent,
            strategies=strategies,
            min_similarity_threshold=config['min_similarity'],
            min_confidence_threshold=config['min_confidence']
        )

    @staticmethod
    def _create_strategies(strategy_names: List[str]) -> List[SimilarityStrategy]:
        """
        Create strategy instances from names.

        WHY: Map string names to strategy objects.
        """
        # Strategy mapping (avoid elif chain)
        strategy_map = {
            'structural': StructuralSimilarityStrategy,
            'semantic': SemanticSimilarityStrategy,
            'ast': ASTSimilarityStrategy,
        }

        strategies = []

        for name in strategy_names:
            strategy_class = strategy_map.get(name.lower())
            if strategy_class:
                strategies.append(strategy_class())

        return strategies
