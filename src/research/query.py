from artemis_logger import get_logger
logger = get_logger('query')
'\nWHY: Handle example querying operations\nRESPONSIBILITY: Query RAG for similar examples\nPATTERNS: Strategy (query operations)\n\nQuery module provides similarity search for research examples.\n'
from typing import List, Dict, Any, Optional
from rag_agent import RAGAgent

class ExampleQuery:
    """
    Handles querying of research examples from RAG.

    WHY: Separates query logic from repository interface.
    RESPONSIBILITY: Search RAG for similar examples with filtering.
    PATTERNS: Strategy (pluggable queries).
    """
    ARTIFACT_TYPE = 'code_example'

    def __init__(self, rag_agent: RAGAgent):
        """
        Initialize query handler.

        Args:
            rag_agent: RAG agent for querying
        """
        self.rag = rag_agent

    def find_similar(self, query: str, top_k: int=5, language_filter: Optional[str]=None) -> List[Dict[str, Any]]:
        """
        Query for similar examples.

        WHY: Semantic search enables finding relevant examples.

        Args:
            query: Search query
            top_k: Number of results
            language_filter: Optional language filter

        Returns:
            List of similar examples with metadata
        """
        filters = {}
        if language_filter:
            filters['language'] = language_filter
        try:
            results = self.rag.query_similar(query_text=query, artifact_types=[self.ARTIFACT_TYPE], top_k=top_k, filters=filters if filters else None)
            return results
        except Exception as e:
            
            logger.log(f'Warning: Failed to query examples: {e}', 'INFO')
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored examples.

        WHY: Monitoring and debugging support.

        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.rag.get_stats()
            return {'total_examples': stats.get('by_type', {}).get(self.ARTIFACT_TYPE, 0), 'total_artifacts': stats.get('total_artifacts', 0), 'database_path': stats.get('database_path', ''), 'chromadb_available': stats.get('chromadb_available', False)}
        except Exception as e:
            return {'total_examples': 0, 'total_artifacts': 0, 'database_path': '', 'chromadb_available': False, 'error': str(e)}