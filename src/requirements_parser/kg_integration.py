from artemis_logger import get_logger
logger = get_logger('kg_integration')
'\nKnowledge Graph Integration\n\nWHY: Separate KG query logic from main parser\nRESPONSIBILITY: Query KG for similar requirements and patterns\nPATTERNS: Repository pattern for KG data access\n'
from typing import Optional, Dict, Any, List

class KnowledgeGraphIntegration:
    """
    Knowledge Graph integration for requirements parsing

    WHY: KG-first approach reduces LLM token usage
    RESPONSIBILITY: Query KG for similar projects and common patterns
    PATTERNS: Repository pattern
    """

    def __init__(self, verbose: bool=False):
        """
        Initialize KG integration

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    def query_kg_for_similar_requirements(self, project_name: str) -> Optional[Dict[str, Any]]:
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
            self.log(f'Could not query KG for similar requirements: {e}')
            return None

    def _query_kg_for_similar_reqs(self, kg: Any) -> Optional[List[Dict[str, Any]]]:
        """
        Query KG for similar requirements

        WHY: Separate query logic for testability
        RESPONSIBILITY: Execute KG query
        """
        similar_requirements = kg.query("\n            MATCH (req:Requirement)\n            WHERE req.status = 'active'\n            RETURN req.req_id, req.title, req.type, req.priority\n            ORDER BY req.priority DESC\n            LIMIT 20\n        ")
        return similar_requirements if similar_requirements else None

    def _build_kg_context_from_requirements(self, similar_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build KG context from similar requirements

        WHY: Transform raw KG data into useful context
        RESPONSIBILITY: Aggregate and summarize KG results

        Args:
            similar_requirements: Raw KG query results

        Returns:
            Structured context dict with patterns and savings estimate
        """
        type_counts = {}
        common_reqs = []
        for req in similar_requirements:
            req_type = req.get('req.type', 'unknown')
            type_counts[req_type] = type_counts.get(req_type, 0) + 1
            common_reqs.append({'req_id': req.get('req.req_id'), 'title': req.get('req.title'), 'type': req_type, 'priority': req.get('req.priority', 'medium')})
        estimated_savings = len(common_reqs) * 50
        return {'similar_projects_count': len(set((req.get('req.req_id', '').split('-')[0] for req in similar_requirements))), 'common_requirements': common_reqs, 'requirement_types': type_counts, 'estimated_token_savings': estimated_savings}

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            
            logger.log(f'[KGIntegration] {message}', 'INFO')