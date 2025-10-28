#!/usr/bin/env python3
"""
Retrospective KG Query Strategy

WHY: Implements KG queries for retrospective analysis based on past sprints.

RESPONSIBILITY:
- Query KG for past retrospective insights
- Extract what went well, what needs improvement, and action items
- Include sprint velocity context
- Estimate token savings (~800 tokens with historical insights)

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


class RetrospectiveKGStrategy(KGQueryStrategy):
    """KG query strategy for retrospective analysis"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for retrospective insights from past sprints"""
        try:
            start = time.time()

            sprint_number = query_params.get('sprint_number', 0)
            team_name = query_params.get('team_name', 'default')

            # Query for past retrospective insights and action items
            retrospective_data = kg.query("""
                MATCH (retro:Retrospective)-[:FOR_SPRINT]->(sprint:Sprint)
                WHERE sprint.team_name = $team_name
                AND sprint.sprint_number < $sprint_number
                RETURN retro.retro_id,
                       retro.what_went_well,
                       retro.what_needs_improvement,
                       retro.action_items,
                       sprint.sprint_number,
                       sprint.velocity
                ORDER BY sprint.sprint_number DESC
                LIMIT 3
            """, {"team_name": team_name, "sprint_number": sprint_number})

            elapsed_ms = (time.time() - start) * 1000

            # Guard clause: No retrospective data found
            if not retrospective_data:
                return KGContext(
                    query_type=QueryType.RETROSPECTIVE,
                    patterns_found=[],
                    pattern_count=0,
                    estimated_token_savings=0,
                    kg_query_time_ms=elapsed_ms,
                    kg_available=True
                )

            patterns = [
                {
                    'retro_id': r.get('retro.retro_id'),
                    'what_went_well': r.get('retro.what_went_well'),
                    'what_needs_improvement': r.get('retro.what_needs_improvement'),
                    'action_items': r.get('retro.action_items'),
                    'sprint_number': r.get('sprint.sprint_number'),
                    'velocity': r.get('sprint.velocity')
                }
                for r in retrospective_data
            ]

            return KGContext(
                query_type=QueryType.RETROSPECTIVE,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for retrospective: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Retrospective can save ~800 tokens with historical insights"""
        return 800 if patterns else 0
