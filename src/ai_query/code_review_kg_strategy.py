#!/usr/bin/env python3
"""
Code Review KG Query Strategy

WHY: Implements KG queries for code review patterns.

RESPONSIBILITY:
- Query KG for similar code reviews by file type
- Extract review patterns (review_id, critical_issues, high_issues)
- Estimate token savings (~2000 tokens with focused patterns)

PATTERNS:
- Strategy Pattern implementation
- Guard clauses for early returns
- Conditional savings estimation
"""

from typing import Dict, List, Any
import time

from artemis_exceptions import KnowledgeGraphError, wrap_exception
from ai_query.kg_query_strategy import KGQueryStrategy
from ai_query.kg_context import KGContext
from ai_query.query_type import QueryType


class CodeReviewKGStrategy(KGQueryStrategy):
    """KG query strategy for code reviews"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for similar code reviews"""
        try:
            start = time.time()

            file_types = query_params.get('file_types', [])

            similar_reviews = []
            for file_type in file_types:
                reviews = kg.query("""
                    MATCH (review:CodeReview)-[:REVIEWED]->(file:File)
                    WHERE file.file_type = $file_type
                    AND review.critical_issues > 0
                    RETURN review.review_id, review.critical_issues, review.high_issues
                    LIMIT 5
                """, {"file_type": file_type})
                if reviews:
                    similar_reviews.extend(reviews)

            elapsed_ms = (time.time() - start) * 1000

            patterns = [
                {
                    'review_id': rev.get('review.review_id'),
                    'critical_issues': rev.get('review.critical_issues'),
                    'high_issues': rev.get('review.high_issues')
                }
                for rev in similar_reviews
            ]

            return KGContext(
                query_type=QueryType.CODE_REVIEW,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for code reviews: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Code review can save ~2000 tokens with focused patterns"""
        return 2000 if patterns else 0
