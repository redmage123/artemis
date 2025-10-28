#!/usr/bin/env python3
"""
Requirements KG Query Strategy

WHY: Implements KG queries specifically for requirements parsing.

RESPONSIBILITY:
- Query KG for similar requirements
- Extract requirement patterns (req_id, title, type, priority)
- Estimate token savings (~50 tokens per pattern)

PATTERNS:
- Strategy Pattern implementation
- Guard clauses for early returns
- Exception wrapping for consistent error handling
"""

from typing import Dict, List, Any
import time

from artemis_exceptions import KnowledgeGraphError, wrap_exception
from ai_query.kg_query_strategy import KGQueryStrategy
from ai_query.kg_context import KGContext
from ai_query.query_type import QueryType


class RequirementsKGStrategy(KGQueryStrategy):
    """KG query strategy for requirements parsing"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for similar requirements"""
        try:
            start = time.time()

            similar_requirements = kg.query("""
                MATCH (req:Requirement)
                WHERE req.status = 'active'
                RETURN req.req_id, req.title, req.type, req.priority
                ORDER BY req.priority DESC
                LIMIT 20
            """)

            elapsed_ms = (time.time() - start) * 1000

            # Guard clause: No requirements found
            if not similar_requirements:
                return KGContext(
                    query_type=QueryType.REQUIREMENTS_PARSING,
                    patterns_found=[],
                    pattern_count=0,
                    estimated_token_savings=0,
                    kg_query_time_ms=elapsed_ms,
                    kg_available=True
                )

            patterns = [
                {
                    'req_id': req.get('req.req_id'),
                    'title': req.get('req.title'),
                    'type': req.get('req.type'),
                    'priority': req.get('req.priority', 'medium')
                }
                for req in similar_requirements
            ]

            return KGContext(
                query_type=QueryType.REQUIREMENTS_PARSING,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for requirements: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Estimate ~50 tokens saved per pattern"""
        return len(patterns) * 50
