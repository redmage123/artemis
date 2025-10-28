#!/usr/bin/env python3
"""
Error Recovery KG Query Strategy

WHY: Implements KG queries for error recovery patterns and solutions.

RESPONSIBILITY:
- Query KG for similar errors and their solutions
- Filter by error type and stage
- Extract solution patterns with success rates
- Estimate token savings (~1000 tokens with known solutions)

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


class ErrorRecoveryKGStrategy(KGQueryStrategy):
    """KG query strategy for error recovery"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for similar errors and their solutions"""
        try:
            start = time.time()

            error_type = query_params.get('error_type', '')
            stage_name = query_params.get('stage_name', '')

            # Query for similar errors
            similar_errors = kg.query("""
                MATCH (error:Error)-[:OCCURRED_IN]->(stage:Stage)
                WHERE error.error_type CONTAINS $error_type
                AND stage.name = $stage_name
                RETURN error.error_type, error.solution, error.success_rate
                ORDER BY error.success_rate DESC
                LIMIT 5
            """, {"error_type": error_type, "stage_name": stage_name})

            elapsed_ms = (time.time() - start) * 1000

            # Guard clause: No errors found
            if not similar_errors:
                return KGContext(
                    query_type=QueryType.ERROR_RECOVERY,
                    patterns_found=[],
                    pattern_count=0,
                    estimated_token_savings=0,
                    kg_query_time_ms=elapsed_ms,
                    kg_available=True
                )

            patterns = [
                {
                    'error_type': e.get('error.error_type'),
                    'solution': e.get('error.solution'),
                    'success_rate': e.get('error.success_rate')
                }
                for e in similar_errors
            ]

            return KGContext(
                query_type=QueryType.ERROR_RECOVERY,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for error recovery: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Error recovery can save ~1000 tokens with known solutions"""
        return 1000 if patterns else 0
