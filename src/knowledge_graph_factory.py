from artemis_logger import get_logger
logger = get_logger('knowledge_graph_factory')
'\nKnowledge Graph Factory - Singleton Pattern for Artemis\n\nProvides centralized access to the Knowledge Graph across all agents.\nEnsures single instance with graceful fallback if Memgraph unavailable.\n\nUsage:\n    from knowledge_graph_factory import get_knowledge_graph\n\n    kg = get_knowledge_graph()\n    if kg:\n        kg.add_file("auth.py", "python")\n'
import os
from typing import Optional
from knowledge_graph import KnowledgeGraph, MEMGRAPH_AVAILABLE

class KnowledgeGraphFactory:
    """
    Singleton factory for Knowledge Graph

    Why this exists: Ensures single shared KnowledgeGraph instance across all
    agents, preventing connection pool exhaustion and maintaining consistency.

    Ensures only one instance exists and provides graceful degradation
    if Memgraph is not available.

    Design Pattern: Singleton + Factory
    Why Singleton: Knowledge Graph represents shared system state (code relationships)
    Why Factory: Encapsulates complex initialization logic and error handling

    Graceful degradation: If Memgraph unavailable, returns None and logs warning
    rather than crashing, allowing Artemis to continue without KG features.
    """
    _instance: Optional[KnowledgeGraph] = None
    _initialization_attempted: bool = False
    _initialization_successful: bool = False

    @classmethod
    def get_instance(cls, host: Optional[str]=None, port: Optional[int]=None) -> Optional[KnowledgeGraph]:
        """
        Get or create singleton Knowledge Graph instance

        Args:
            host: Memgraph host (default: localhost or MEMGRAPH_HOST env var)
            port: Memgraph port (default: 7687 or MEMGRAPH_PORT env var)

        Returns:
            KnowledgeGraph instance or None if unavailable
        """
        if cls._instance is not None:
            return cls._instance
        if cls._initialization_attempted and (not cls._initialization_successful):
            return None
        cls._initialization_attempted = True
        if not MEMGRAPH_AVAILABLE:
            
            logger.log('⚠️  Knowledge Graph unavailable: gqlalchemy not installed', 'INFO')
            
            logger.log('   Install with: pip install gqlalchemy', 'INFO')
            
            logger.log('   Agents will continue without knowledge graph integration', 'INFO')
            return None
        if host is None:
            host = os.getenv('MEMGRAPH_HOST', 'localhost')
        if port is None:
            port = int(os.getenv('MEMGRAPH_PORT', '7687'))
        try:
            cls._instance = KnowledgeGraph(host=host, port=port)
            cls._initialization_successful = True
            
            logger.log(f'✅ Knowledge Graph connected: {host}:{port}', 'INFO')
            return cls._instance
        except Exception as e:
            
            logger.log(f'⚠️  Knowledge Graph connection failed: {e}', 'INFO')
            
            logger.log(f'   Host: {host}, Port: {port}', 'INFO')
            
            logger.log('   Agents will continue without knowledge graph integration', 'INFO')
            
            logger.log('   To enable, ensure Memgraph is running:', 'INFO')
            
            logger.log('     docker run -p 7687:7687 memgraph/memgraph', 'INFO')
            cls._initialization_successful = False
            return None

    @classmethod
    def reset(cls) -> None:
        """Reset singleton instance (useful for testing)"""
        cls._instance = None
        cls._initialization_attempted = False
        cls._initialization_successful = False

    @classmethod
    def is_available(cls) -> bool:
        """Check if Knowledge Graph is available"""
        return cls._initialization_successful and cls._instance is not None

def get_knowledge_graph(host: Optional[str]=None, port: Optional[int]=None) -> Optional[KnowledgeGraph]:
    """
    Get Knowledge Graph instance (convenience function)

    Args:
        host: Memgraph host (optional)
        port: Memgraph port (optional)

    Returns:
        KnowledgeGraph instance or None
    """
    return KnowledgeGraphFactory.get_instance(host=host, port=port)

def is_knowledge_graph_available() -> bool:
    """
    Check if Knowledge Graph is available

    Returns:
        True if available, False otherwise
    """
    return KnowledgeGraphFactory.is_available()