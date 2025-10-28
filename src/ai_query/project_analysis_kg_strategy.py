#!/usr/bin/env python3
"""
Project Analysis KG Query Strategy

WHY: Implements KG queries for project analysis patterns.

RESPONSIBILITY:
- Query KG for similar project analyses
- Extract critical/high severity issues
- Estimate token savings (~1500 tokens with known patterns)

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


class ProjectAnalysisKGStrategy(KGQueryStrategy):
    """KG query strategy for project analysis"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for similar project analyses"""
        try:
            start = time.time()

            # Query for similar projects and their common issues
            similar_analyses = kg.query("""
                MATCH (analysis:ProjectAnalysis)-[:IDENTIFIED]->(issue:Issue)
                WHERE issue.severity IN ['CRITICAL', 'HIGH']
                RETURN analysis.project_name, issue.category, issue.severity,
                       issue.description
                ORDER BY issue.severity DESC
                LIMIT 10
            """)

            elapsed_ms = (time.time() - start) * 1000

            # Guard clause: No analyses found
            if not similar_analyses:
                return KGContext(
                    query_type=QueryType.PROJECT_ANALYSIS,
                    patterns_found=[],
                    pattern_count=0,
                    estimated_token_savings=0,
                    kg_query_time_ms=elapsed_ms,
                    kg_available=True
                )

            patterns = [
                {
                    'project_name': a.get('analysis.project_name'),
                    'category': a.get('issue.category'),
                    'severity': a.get('issue.severity'),
                    'description': a.get('issue.description')
                }
                for a in similar_analyses
            ]

            return KGContext(
                query_type=QueryType.PROJECT_ANALYSIS,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for project analysis: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Project analysis can save ~1500 tokens with known patterns"""
        return 1500 if patterns else 0
