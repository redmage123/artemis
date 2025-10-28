#!/usr/bin/env python3
"""
WHY: Maintain backward compatibility with existing code using rag_agent.py.
     Delegates to modular rag package while preserving original interface.

RESPONSIBILITY:
- Provide drop-in replacement for original RAGAgent class
- Delegate all operations to rag.RAGEngine
- Support DebugMixin integration for existing code

PATTERNS:
- Adapter Pattern: Adapt new RAGEngine to old RAGAgent interface
- Proxy Pattern: Proxy calls to underlying engine
- Facade Pattern: Simplify access to refactored package
"""

from typing import Dict, List, Optional, Any
from debug_mixin import DebugMixin
from rag import RAGEngine, ARTIFACT_TYPES, create_rag_agent


class RAGAgent(DebugMixin):
    """
    Backward-compatible RAG Agent wrapper.

    Delegates to rag.RAGEngine while maintaining original interface.
    This allows existing code to work without modifications.
    """

    # Export artifact types for backward compatibility
    ARTIFACT_TYPES = ARTIFACT_TYPES

    def __init__(self, db_path: str = "db", verbose: bool = True):
        """
        Initialize RAG Agent with database path.

        Args:
            db_path: Path to RAG database (default: 'db' relative to .agents/agile)
            verbose: Enable verbose logging
        """
        DebugMixin.__init__(self, component_name="rag")
        self.engine = RAGEngine(db_path=db_path, verbose=verbose)

        # Expose engine attributes for compatibility
        self.db_path = self.engine.db_path
        self.verbose = self.engine.verbose
        self.collections = getattr(self.engine.vector_store, 'collections', {})
        self.client = getattr(self.engine.vector_store, 'client', None)

        self.debug_log(
            "RAGAgent initialized (delegating to RAGEngine)",
            db_path=str(self.db_path),
            chromadb_available=self.engine.vector_store.chromadb_available
        )

    def log(self, message: str):
        """Log message if verbose."""
        self.engine.log(message)

    def store_artifact(
        self,
        artifact_type: str,
        card_id: str,
        task_title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
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
        self.debug_trace("store_artifact", artifact_type=artifact_type, card_id=card_id)
        return self.engine.store_artifact(
            artifact_type=artifact_type,
            card_id=card_id,
            task_title=task_title,
            content=content,
            metadata=metadata
        )

    def query_similar(
        self,
        query_text: str,
        artifact_types: Optional[List[str]] = None,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
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
        self.debug_if_enabled("rag_queries", "Querying RAG", query=query_text[:50], top_k=top_k)
        return self.engine.query_similar(
            query_text=query_text,
            artifact_types=artifact_types,
            top_k=top_k,
            filters=filters
        )

    def get_recommendations(
        self,
        task_description: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Get RAG-informed recommendations based on past experience.

        Args:
            task_description: Description of new task
            context: Additional context (technologies, priority, etc.)

        Returns:
            Dict with recommendations based on history
        """
        return self.engine.get_recommendations(
            task_description=task_description,
            context=context
        )

    def extract_patterns(
        self,
        pattern_type: str = "technology_success_rates",
        time_window_days: int = 90
    ) -> Dict:
        """
        Extract learning patterns from stored artifacts.

        Args:
            pattern_type: Type of pattern to extract
            time_window_days: Time window for analysis

        Returns:
            Dict with extracted patterns
        """
        return self.engine.extract_patterns(
            pattern_type=pattern_type,
            time_window_days=time_window_days
        )

    def get_stats(self) -> Dict:
        """Get RAG database statistics."""
        return self.engine.get_stats()

    def search_code_examples(
        self,
        query: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
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
        return self.engine.search_code_examples(
            query=query,
            language=language,
            framework=framework,
            top_k=top_k
        )


# Convenience functions for backward compatibility
def create_rag_agent(db_path: str = "db") -> RAGAgent:
    """
    Create RAG agent instance.

    Args:
        db_path: Path to RAG database (default: 'db' relative to .agents/agile)

    Returns:
        Initialized RAGAgent instance
    """
    return RAGAgent(db_path=db_path)


if __name__ == "__main__":
    # Example usage
    print("RAG Agent - Example Usage")
    print("=" * 60)

    # Create agent
    rag = RAGAgent()

    # Store research report
    rag.store_artifact(
        artifact_type="research_report",
        card_id="card-123",
        task_title="Add OAuth authentication",
        content="""
        Research Report: OAuth Authentication

        Recommendation: Use authlib library
        - GitHub stars: 4.3k
        - Actively maintained
        - Best documentation

        Critical finding: Must encrypt tokens in database
        """,
        metadata={
            "technologies": ["authlib", "OAuth2", "Flask"],
            "recommendations": ["Use authlib", "Encrypt tokens"],
            "confidence": "HIGH"
        }
    )

    # Store ADR
    rag.store_artifact(
        artifact_type="architecture_decision",
        card_id="card-123",
        task_title="Add OAuth authentication",
        content="""
        ADR-003: OAuth Authentication

        Decision: Use authlib + Flask-Login
        Reasoning: Based on research showing authlib is most maintained
        """,
        metadata={
            "adr_number": "003",
            "technologies": ["authlib", "Flask-Login"],
            "decision": "Use authlib"
        }
    )

    # Query similar
    print("\n📊 Querying for OAuth-related artifacts...")
    results = rag.query_similar("OAuth library selection", top_k=5)

    for result in results:
        print(f"\n  Found: {result['artifact_type']}")
        print(f"  Card: {result.get('metadata', {}).get('card_id')}")
        print(f"  Similarity: {result['similarity']:.2f}")

    # Get recommendations
    print("\n💡 Getting recommendations for new OAuth task...")
    recommendations = rag.get_recommendations(
        task_description="Add GitHub OAuth login",
        context={"technologies": ["OAuth", "GitHub"]}
    )

    print(f"\n  Based on history:")
    for item in recommendations['based_on_history']:
        print(f"    - {item}")

    print(f"\n  Recommendations:")
    for item in recommendations['recommendations']:
        print(f"    - {item}")

    # Get stats
    print("\n📈 RAG Database Statistics:")
    stats = rag.get_stats()
    print(f"  Total artifacts: {stats['total_artifacts']}")
    print(f"  By type:")
    for artifact_type, count in stats['by_type'].items():
        if count > 0:
            print(f"    - {artifact_type}: {count}")

    print("\n" + "=" * 60)
    print("✅ Example complete!")
