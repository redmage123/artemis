#!/usr/bin/env python3
"""
Architecture KG Query Strategy

WHY: Implements KG queries for architecture decisions (ADRs).

RESPONSIBILITY:
- Query KG for similar ADRs based on keywords
- Extract ADR patterns (adr_id, title)
- Remove duplicate ADRs
- Estimate token savings (~200 tokens per ADR)

PATTERNS:
- Strategy Pattern implementation
- Guard clauses for early returns
- Deduplication using dict comprehension
"""

from typing import Dict, List, Any
import time

from artemis_exceptions import KnowledgeGraphError, wrap_exception
from ai_query.kg_query_strategy import KGQueryStrategy
from ai_query.kg_context import KGContext
from ai_query.query_type import QueryType


class ArchitectureKGStrategy(KGQueryStrategy):
    """KG query strategy for architecture decisions"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for similar ADRs"""
        try:
            start = time.time()

            keywords = query_params.get('keywords', [])
            req_type = query_params.get('req_type', 'functional')

            similar_adrs = []
            for keyword in keywords[:3]:  # Top 3 keywords
                adrs = kg.query("""
                    MATCH (adr:ADR)-[:ADDRESSES]->(req:Requirement)
                    WHERE req.title CONTAINS $keyword OR req.type = $req_type
                    RETURN DISTINCT adr.adr_id, adr.title
                    LIMIT 3
                """, {"keyword": keyword, "req_type": req_type})
                if adrs:
                    similar_adrs.extend(adrs)

            elapsed_ms = (time.time() - start) * 1000

            patterns = [
                {
                    'adr_id': adr.get('adr.adr_id'),
                    'title': adr.get('adr.title')
                }
                for adr in similar_adrs
            ]

            # Remove duplicates
            unique_patterns = {p['adr_id']: p for p in patterns}.values()
            patterns = list(unique_patterns)

            return KGContext(
                query_type=QueryType.ARCHITECTURE_DESIGN,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for ADRs: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Estimate ~200 tokens saved per ADR pattern"""
        return len(patterns) * 200
