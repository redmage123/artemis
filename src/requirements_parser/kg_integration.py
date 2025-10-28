#!/usr/bin/env python3
"""
Knowledge Graph Integration

WHY: Separate KG query logic from main parser
RESPONSIBILITY: Query KG for similar requirements and patterns
PATTERNS: Repository pattern for KG data access
"""

from typing import Optional, Dict, Any, List


class KnowledgeGraphIntegration:
    """
    Knowledge Graph integration for requirements parsing

    WHY: KG-first approach reduces LLM token usage
    RESPONSIBILITY: Query KG for similar projects and common patterns
    PATTERNS: Repository pattern
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize KG integration

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    def query_kg_for_similar_requirements(
        self,
        project_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Query Knowledge Graph for similar projects and common requirement patterns

        WHY: KG-first approach reduces LLM token usage by providing context
        RESPONSIBILITY: Find relevant patterns from historical data

        Args:
            project_name: Project name for similarity matching

        Returns:
            Dict with similar project info and common requirements, or None if KG unavailable
        """
        try:
            from knowledge_graph_factory import get_knowledge_graph
            kg = get_knowledge_graph()

            if not kg:
                return None

            similar_requirements = self._query_kg_for_similar_reqs(kg)
            if not similar_requirements:
                return None

            return self._build_kg_context_from_requirements(similar_requirements)

        except Exception as e:
            self.log(f"Could not query KG for similar requirements: {e}")
            return None

    def _query_kg_for_similar_reqs(self, kg: Any) -> Optional[List[Dict[str, Any]]]:
        """
        Query KG for similar requirements

        WHY: Separate query logic for testability
        RESPONSIBILITY: Execute KG query
        """
        similar_requirements = kg.query("""
            MATCH (req:Requirement)
            WHERE req.status = 'active'
            RETURN req.req_id, req.title, req.type, req.priority
            ORDER BY req.priority DESC
            LIMIT 20
        """)
        return similar_requirements if similar_requirements else None

    def _build_kg_context_from_requirements(
        self,
        similar_requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build KG context from similar requirements

        WHY: Transform raw KG data into useful context
        RESPONSIBILITY: Aggregate and summarize KG results

        Args:
            similar_requirements: Raw KG query results

        Returns:
            Structured context dict with patterns and savings estimate
        """
        # Group by type to find common patterns
        type_counts = {}
        common_reqs = []

        for req in similar_requirements:
            req_type = req.get('req.type', 'unknown')
            type_counts[req_type] = type_counts.get(req_type, 0) + 1

            common_reqs.append({
                'req_id': req.get('req.req_id'),
                'title': req.get('req.title'),
                'type': req_type,
                'priority': req.get('req.priority', 'medium')
            })

        # Estimate token savings:
        # - Providing 5 common requirements as hints ~= 200 tokens
        # - This helps LLM avoid re-generating similar patterns
        # - Estimated savings: ~500-1000 tokens (LLM doesn't need to "invent" common NFRs)
        estimated_savings = len(common_reqs) * 50  # Conservative estimate

        return {
            'similar_projects_count': len(set(req.get('req.req_id', '').split('-')[0] for req in similar_requirements)),
            'common_requirements': common_reqs,
            'requirement_types': type_counts,
            'estimated_token_savings': estimated_savings
        }

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(f"[KGIntegration] {message}")
