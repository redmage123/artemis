from artemis_logger import get_logger
logger = get_logger('rag_agent')
'\nWHY: Maintain backward compatibility with existing code using rag_agent.py.\n     Delegates to modular rag package while preserving original interface.\n\nRESPONSIBILITY:\n- Provide drop-in replacement for original RAGAgent class\n- Delegate all operations to rag.RAGEngine\n- Support DebugMixin integration for existing code\n\nPATTERNS:\n- Adapter Pattern: Adapt new RAGEngine to old RAGAgent interface\n- Proxy Pattern: Proxy calls to underlying engine\n- Facade Pattern: Simplify access to refactored package\n'
from typing import Dict, List, Optional, Any
from debug_mixin import DebugMixin
from rag import RAGEngine, ARTIFACT_TYPES, create_rag_agent

class RAGAgent(DebugMixin):
    """
    Backward-compatible RAG Agent wrapper.

    Delegates to rag.RAGEngine while maintaining original interface.
    This allows existing code to work without modifications.
    """
    ARTIFACT_TYPES = ARTIFACT_TYPES

    def __init__(self, db_path: str='db', verbose: bool=True):
        """
        Initialize RAG Agent with database path.

        Args:
            db_path: Path to RAG database (default: 'db' relative to .agents/agile)
            verbose: Enable verbose logging
        """
        DebugMixin.__init__(self, component_name='rag')
        self.engine = RAGEngine(db_path=db_path, verbose=verbose)
        self.db_path = self.engine.db_path
        self.verbose = self.engine.verbose
        self.collections = getattr(self.engine.vector_store, 'collections', {})
        self.client = getattr(self.engine.vector_store, 'client', None)
        self.debug_log('RAGAgent initialized (delegating to RAGEngine)', db_path=str(self.db_path), chromadb_available=self.engine.vector_store.chromadb_available)

    def log(self, message: str):
        """Log message if verbose."""
        self.engine.log(message)

    def store_artifact(self, artifact_type: str, card_id: str, task_title: str, content: str, metadata: Optional[Dict]=None) -> str:
        """
        Store artifact in RAG database.

        Args:
            artifact_type: Type of artifact (research_report, adr, etc.)
            card_id: Card ID
            task_title: Task title
            content: Full content text
            metadata: Additional metadata

        Returns:
            Artifact ID
        """
        self.debug_trace('store_artifact', artifact_type=artifact_type, card_id=card_id)
        return self.engine.store_artifact(artifact_type=artifact_type, card_id=card_id, task_title=task_title, content=content, metadata=metadata)

    def query_similar(self, query_text: str, artifact_types: Optional[List[str]]=None, top_k: int=5, filters: Optional[Dict]=None) -> List[Dict]:
        """
        Query for similar artifacts using semantic search.

        Args:
            query_text: Query text for semantic search
            artifact_types: Types to search (None = all)
            top_k: Number of results to return
            filters: Metadata filters

        Returns:
            List of similar artifacts
        """
        self.debug_if_enabled('rag_queries', 'Querying RAG', query=query_text[:50], top_k=top_k)
        return self.engine.query_similar(query_text=query_text, artifact_types=artifact_types, top_k=top_k, filters=filters)

    def get_recommendations(self, task_description: str, context: Optional[Dict]=None) -> Dict:
        """
        Get RAG-informed recommendations based on past experience.

        Args:
            task_description: Description of new task
            context: Additional context (technologies, priority, etc.)

        Returns:
            Dict with recommendations based on history
        """
        return self.engine.get_recommendations(task_description=task_description, context=context)

    def extract_patterns(self, pattern_type: str='technology_success_rates', time_window_days: int=90) -> Dict:
        """
        Extract learning patterns from stored artifacts.

        Args:
            pattern_type: Type of pattern to extract
            time_window_days: Time window for analysis

        Returns:
            Dict with extracted patterns
        """
        return self.engine.extract_patterns(pattern_type=pattern_type, time_window_days=time_window_days)

    def get_stats(self) -> Dict:
        """Get RAG database statistics."""
        return self.engine.get_stats()

    def search_code_examples(self, query: str, language: Optional[str]=None, framework: Optional[str]=None, top_k: int=5) -> List[Dict]:
        """
        Search for code examples in RAG database.

        Args:
            query: Code snippet or description to search for
            language: Filter by programming language (python, ruby, etc.)
            framework: Filter by framework (django, rails, react, etc.)
            top_k: Number of results to return

        Returns:
            List of code examples with metadata
        """
        return self.engine.search_code_examples(query=query, language=language, framework=framework, top_k=top_k)

    def _initialize_collections(self):
        """
        Initialize ChromaDB collections for all artifact types.

        WHY: PromptManager needs to ensure collections exist before storing prompts.
        RESPONSIBILITY: Delegate to underlying vector_store.
        PATTERNS: Delegation pattern - RAGAgent delegates to VectorStore.
        """
        if hasattr(self.engine, 'vector_store') and hasattr(self.engine.vector_store, '_initialize_collections'):
            return self.engine.vector_store._initialize_collections()
        return {}

def create_rag_agent(db_path: str='db') -> RAGAgent:
    """
    Create RAG agent instance.

    Args:
        db_path: Path to RAG database (default: 'db' relative to .agents/agile)

    Returns:
        Initialized RAGAgent instance
    """
    return RAGAgent(db_path=db_path)
if __name__ == '__main__':
    
    logger.log('RAG Agent - Example Usage', 'INFO')
    
    logger.log('=' * 60, 'INFO')
    rag = RAGAgent()
    rag.store_artifact(artifact_type='research_report', card_id='card-123', task_title='Add OAuth authentication', content='\n        Research Report: OAuth Authentication\n\n        Recommendation: Use authlib library\n        - GitHub stars: 4.3k\n        - Actively maintained\n        - Best documentation\n\n        Critical finding: Must encrypt tokens in database\n        ', metadata={'technologies': ['authlib', 'OAuth2', 'Flask'], 'recommendations': ['Use authlib', 'Encrypt tokens'], 'confidence': 'HIGH'})
    rag.store_artifact(artifact_type='architecture_decision', card_id='card-123', task_title='Add OAuth authentication', content='\n        ADR-003: OAuth Authentication\n\n        Decision: Use authlib + Flask-Login\n        Reasoning: Based on research showing authlib is most maintained\n        ', metadata={'adr_number': '003', 'technologies': ['authlib', 'Flask-Login'], 'decision': 'Use authlib'})
    
    logger.log('\n📊 Querying for OAuth-related artifacts...', 'INFO')
    results = rag.query_similar('OAuth library selection', top_k=5)
    for result in results:
        
        logger.log(f"\n  Found: {result['artifact_type']}", 'INFO')
        
        logger.log(f"  Card: {result.get('metadata', {}).get('card_id')}", 'INFO')
        
        logger.log(f"  Similarity: {result['similarity']:.2f}", 'INFO')
    
    logger.log('\n💡 Getting recommendations for new OAuth task...', 'INFO')
    recommendations = rag.get_recommendations(task_description='Add GitHub OAuth login', context={'technologies': ['OAuth', 'GitHub']})
    
    logger.log(f'\n  Based on history:', 'INFO')
    for item in recommendations['based_on_history']:
        
        logger.log(f'    - {item}', 'INFO')
    
    logger.log(f'\n  Recommendations:', 'INFO')
    for item in recommendations['recommendations']:
        
        logger.log(f'    - {item}', 'INFO')
    
    logger.log('\n📈 RAG Database Statistics:', 'INFO')
    stats = rag.get_stats()
    
    logger.log(f"  Total artifacts: {stats['total_artifacts']}", 'INFO')
    
    logger.log(f'  By type:', 'INFO')
    for artifact_type, count in stats['by_type'].items():
        if count > 0:
            
            logger.log(f'    - {artifact_type}: {count}', 'INFO')
    
    logger.log('\n' + '=' * 60, 'INFO')
    
    logger.log('✅ Example complete!', 'INFO')