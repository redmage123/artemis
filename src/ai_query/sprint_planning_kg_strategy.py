#!/usr/bin/env python3
"""
Sprint Planning KG Query Strategy

WHY: Implements KG queries for sprint planning based on historical velocity.

RESPONSIBILITY:
- Query KG for historical sprint data
- Extract velocity and task completion metrics
- Calculate average story points
- Estimate token savings (~1200 tokens with historical data)

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


class SprintPlanningKGStrategy(KGQueryStrategy):
    """KG query strategy for sprint planning"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for sprint planning patterns and velocity data"""
        try:
            start = time.time()

            sprint_number = query_params.get('sprint_number', 0)
            team_name = query_params.get('team_name', 'default')

            # Query for historical sprint data (velocity, completed stories)
            sprint_history = kg.query("""
                MATCH (sprint:Sprint)-[:COMPLETED]->(task:Task)
                WHERE sprint.team_name = $team_name
                AND sprint.sprint_number < $sprint_number
                RETURN sprint.sprint_number, sprint.velocity,
                       COUNT(task) as tasks_completed,
                       AVG(task.story_points) as avg_story_points
                ORDER BY sprint.sprint_number DESC
                LIMIT 5
            """, {"team_name": team_name, "sprint_number": sprint_number})

            elapsed_ms = (time.time() - start) * 1000

            # Guard clause: No sprint history found
            if not sprint_history:
                return KGContext(
                    query_type=QueryType.SPRINT_PLANNING,
                    patterns_found=[],
                    pattern_count=0,
                    estimated_token_savings=0,
                    kg_query_time_ms=elapsed_ms,
                    kg_available=True
                )

            patterns = [
                {
                    'sprint_number': s.get('sprint.sprint_number'),
                    'velocity': s.get('sprint.velocity'),
                    'tasks_completed': s.get('tasks_completed'),
                    'avg_story_points': s.get('avg_story_points')
                }
                for s in sprint_history
            ]

            return KGContext(
                query_type=QueryType.SPRINT_PLANNING,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for sprint planning: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Sprint planning can save ~1200 tokens with historical velocity data"""
        return 1200 if patterns else 0
