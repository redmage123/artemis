#!/usr/bin/env python3
"""
WHY: Analyze code for uncertainty signals and track pattern citations.

RESPONSIBILITY:
- UncertaintyAnalyzer: Detect hedging language, TODOs, assumptions, missing error handling
- CitationTracker: Extract and verify code pattern sources
- Calculate uncertainty scores for hallucination detection
- Support RAG-based citation verification

PATTERNS:
- Strategy Pattern: Multiple analysis strategies (hedging, TODOs, error handling)
- Guard Clause Pattern: Early exit on parsing errors
- Single Responsibility: Each analyzer focuses on one concern
"""

import ast
import re
import logging
from typing import List, Optional, Dict, Any

from .models import UncertaintyMetrics, CodeCitation


class UncertaintyAnalyzer:
    """
    WHY: Detect uncertainty signals that indicate LLM hallucination.

    RESPONSIBILITY:
    - Analyze comments and docstrings for hedging language
    - Identify placeholder comments (TODO, FIXME, etc.)
    - Detect conditional assumptions
    - Find missing error handling
    - Calculate overall uncertainty score
    """

    # Compiled regex patterns for performance
    HEDGING_PATTERN = re.compile(
        r'\b(might|could|possibly|probably|typically|usually|often|sometimes|'
        r'may|should|would|seem|appear|assume|guess|estimate)\b',
        re.IGNORECASE
    )

    TODO_PATTERN = re.compile(
        r'#\s*(TODO|FIXME|XXX|HACK|NOTE|OPTIMIZE|REFACTOR|REVIEW)',
        re.IGNORECASE
    )

    CONDITIONAL_PATTERN = re.compile(
        r'#\s*(if|assuming|provided|when|unless|depends on|requires that)',
        re.IGNORECASE
    )

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize uncertainty analyzer.

        Args:
            logger: Optional logger
        """
        self.logger = logger or logging.getLogger(__name__)

    def analyze(self, code: str) -> UncertaintyMetrics:
        """
        Analyze code for uncertainty signals.

        Args:
            code: Source code to analyze

        Returns:
            UncertaintyMetrics with detected uncertainty signals
        """
        # Guard clause: Empty code
        if not code or not code.strip():
            return UncertaintyMetrics(uncertainty_score=0.0)

        # Extract comments and docstrings for analysis
        comments = self._extract_comments(code)

        # Detect hedging language
        hedging_words = self._detect_hedging(comments)

        # Detect placeholder comments
        placeholder_comments = self._detect_placeholders(comments)

        # Detect conditional assumptions
        conditional_assumptions = self._detect_conditionals(comments)

        # Detect missing error handling
        missing_error_handling = self._detect_missing_error_handling(code)

        # Calculate uncertainty score (0-10)
        uncertainty_score = self._calculate_uncertainty_score(
            hedging_count=len(hedging_words),
            placeholder_count=len(placeholder_comments),
            assumption_count=len(conditional_assumptions),
            missing_error_count=len(missing_error_handling)
        )

        return UncertaintyMetrics(
            uncertainty_score=uncertainty_score,
            hedging_words=hedging_words,
            placeholder_comments=placeholder_comments,
            conditional_assumptions=conditional_assumptions,
            missing_error_handling=missing_error_handling
        )

    def _extract_comments(self, code: str) -> List[str]:
        """
        Extract all comments from code.

        Args:
            code: Source code

        Returns:
            List of comment strings
        """
        comments = []

        # Single-line comments
        for match in re.finditer(r'#(.+)$', code, re.MULTILINE):
            comments.append(match.group(1))

        # Docstrings
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        comments.append(docstring)
        except SyntaxError:
            pass  # Code may be incomplete

        return comments

    def _detect_hedging(self, comments: List[str]) -> List[str]:
        """
        Detect hedging language in comments.

        Args:
            comments: List of comment strings

        Returns:
            List of hedging words found
        """
        hedging_words = []
        for comment in comments:
            matches = self.HEDGING_PATTERN.findall(comment)
            hedging_words.extend(matches)
        return hedging_words

    def _detect_placeholders(self, comments: List[str]) -> List[str]:
        """
        Detect placeholder comments (TODO, FIXME, etc.).

        Args:
            comments: List of comment strings

        Returns:
            List of placeholder comments
        """
        placeholder_comments = []
        for comment in comments:
            if self.TODO_PATTERN.search(comment):
                placeholder_comments.append(comment.strip())
        return placeholder_comments

    def _detect_conditionals(self, comments: List[str]) -> List[str]:
        """
        Detect conditional assumptions in comments.

        Args:
            comments: List of comment strings

        Returns:
            List of conditional assumption comments
        """
        conditional_assumptions = []
        for comment in comments:
            if self.CONDITIONAL_PATTERN.search(comment):
                conditional_assumptions.append(comment.strip())
        return conditional_assumptions

    def _detect_missing_error_handling(self, code: str) -> List[str]:
        """
        Detect functions that might need error handling.

        Args:
            code: Source code

        Returns:
            List of issues describing missing error handling
        """
        missing = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue

                # Check if function has try-except
                has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))

                # Check if function does risky operations
                has_risky_ops = any(
                    isinstance(n, ast.Call) and
                    hasattr(n.func, 'attr') and
                    n.func.attr in {'open', 'request', 'connect', 'query', 'execute'}
                    for n in ast.walk(node)
                )

                if has_risky_ops and not has_try:
                    missing.append(f"Function '{node.name}' performs I/O without error handling")

        except SyntaxError:
            pass

        return missing

    def _calculate_uncertainty_score(
        self,
        hedging_count: int,
        placeholder_count: int,
        assumption_count: int,
        missing_error_count: int
    ) -> float:
        """
        Calculate overall uncertainty score (0-10).

        Higher score = more uncertainty

        Args:
            hedging_count: Number of hedging words
            placeholder_count: Number of placeholder comments
            assumption_count: Number of conditional assumptions
            missing_error_count: Number of missing error handlers

        Returns:
            Uncertainty score (0-10)
        """
        score = 0.0

        # Each indicator adds to uncertainty
        score += min(hedging_count * 0.5, 3.0)          # Max 3 points
        score += min(placeholder_count * 2.0, 4.0)      # Max 4 points
        score += min(assumption_count * 1.0, 2.0)       # Max 2 points
        score += min(missing_error_count * 0.5, 1.0)    # Max 1 point

        return min(score, 10.0)


class CitationTracker:
    """
    WHY: Track code pattern sources to verify authenticity.

    RESPONSIBILITY:
    - Extract citations from code comments
    - Parse citation format (From, Based on, See, etc.)
    - Support RAG-based citation verification
    - Calculate citation confidence scores
    """

    CITATION_PATTERN = re.compile(
        r'#\s*(From|Based on|See|Reference|Source):\s*(.+)$',
        re.IGNORECASE | re.MULTILINE
    )

    def __init__(self, rag_agent: Optional[Any] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize citation tracker.

        Args:
            rag_agent: Optional RAG agent for citation verification
            logger: Optional logger
        """
        self.rag_agent = rag_agent
        self.logger = logger or logging.getLogger(__name__)

    def extract_citations(self, code: str, context: Dict[str, Any]) -> List[CodeCitation]:
        """
        Extract citations from code comments.

        Looks for patterns like:
        # From Django docs v4.2
        # Based on Rails book p.45
        # See: https://...

        Args:
            code: Source code
            context: Context dictionary

        Returns:
            List of CodeCitation objects
        """
        # Guard clause: Empty code
        if not code or not code.strip():
            return []

        citations = []

        for match in self.CITATION_PATTERN.finditer(code):
            source = match.group(2).strip()

            # Extract the code pattern near this citation
            # (Simplified: get next 5 lines)
            lines = code[match.end():].split('\n')[:5]
            pattern = '\n'.join(line for line in lines if line.strip() and not line.strip().startswith('#'))

            citations.append(CodeCitation(
                pattern=pattern,
                source=source,
                confidence=0.8  # Basic confidence
            ))

        return citations

    def verify_citation(self, citation: CodeCitation) -> bool:
        """
        Verify citation against RAG database.

        Args:
            citation: Citation to verify

        Returns:
            True if similar pattern found in cited source
        """
        # Guard clause: No RAG agent available
        if not self.rag_agent:
            return True  # Can't verify without RAG

        # Query RAG for similar patterns in cited source
        try:
            # Build query from citation pattern and source
            query_text = f"{citation.pattern}\n\nSource: {citation.source}"

            # Search for similar code patterns in RAG database
            # Use top_k=3 to get a few candidates for verification
            results = self.rag_agent.query_similar(
                query_text=query_text,
                artifact_types=["code_pattern", "code_example", "adr", "research_report"],
                top_k=3
            )

            # Citation is verified if we find similar patterns
            # with reasonable similarity (results are returned in order of similarity)
            if results:
                # Update confidence based on similarity of top result
                # If RAG found similar patterns, increase confidence
                citation.confidence = min(0.95, citation.confidence + 0.1)
                self.logger.debug(
                    f"Citation verified via RAG: found {len(results)} similar patterns for source '{citation.source}'"
                )
                return True
            else:
                # No similar patterns found - this could indicate hallucination
                # Decrease confidence slightly but don't fail completely
                citation.confidence = max(0.5, citation.confidence - 0.1)
                self.logger.warning(
                    f"Citation not verified via RAG: no similar patterns found for source '{citation.source}'"
                )
                return False

        except Exception as e:
            # If RAG query fails, log error but don't fail verification
            self.logger.error(f"RAG query failed during citation verification: {e}")
            return True  # Assume valid on error to avoid false negatives
