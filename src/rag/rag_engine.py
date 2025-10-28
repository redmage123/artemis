#!/usr/bin/env python3
"""
WHY: Orchestrate all RAG operations through a unified high-level interface.
     Provides the main entry point for storing and retrieving artifacts.

RESPONSIBILITY:
- Coordinate vector store, retriever, and pattern analyzer
- Provide high-level API for artifact storage and retrieval
- Manage logging and debugging across components
- Generate statistics and health metrics

PATTERNS:
- Facade Pattern: Simplify complex subsystem interactions
- Dependency Injection: Inject dependencies for testability
- Template Method Pattern: Define RAG operation flow
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from rag.models import ARTIFACT_TYPES, create_artifact
from rag.document_processor import (
    generate_artifact_id,
    prepare_artifact_metadata
)
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.pattern_analyzer import PatternAnalyzer


class RAGEngine:
    """
    Main RAG orchestration engine.

    Coordinates storage, retrieval, and analysis operations.
    """

    def __init__(
        self,
        db_path: str = "db",
        verbose: bool = True
    ):
        """
        Initialize RAG engine.

        Args:
            db_path: Path to RAG database (default: 'db')
            verbose: Enable verbose logging
        """
        self.verbose = verbose

        # Convert to absolute path if relative
        self.db_path = Path(db_path)
        if not self.db_path.is_absolute():
            script_dir = Path(__file__).parent.parent
            self.db_path = script_dir / self.db_path

        self.db_path.mkdir(exist_ok=True, parents=True)

        # Initialize components
        self.vector_store = VectorStore(self.db_path, self.log)
        self.retriever = Retriever(self.vector_store, self.log)
        self.pattern_analyzer = PatternAnalyzer(self.retriever.query_similar, self.log)

        self.log("RAG Engine initialized")
        self.log(f"Database path: {self.db_path}")

    def log(self, message: str):
        """Log message if verbose enabled."""
        if not self.verbose:
            return

        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        print(f"[{timestamp}] [RAG] {message}")

    def store_artifact(
        self,
        artifact_type: str,
        card_id: str,
        task_title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store artifact in RAG database.

        Args:
            artifact_type: Type of artifact (research_report, adr, etc.)
            card_id: Card ID
            task_title: Task title
            content: Full content text
            metadata: Additional metadata

        Returns:
            Artifact ID or None if failed
        """
        # Guard: Validate artifact type
        if artifact_type not in ARTIFACT_TYPES:
            self.log(f"⚠️  Unknown artifact type: {artifact_type}")
            return None

        # Generate artifact ID
        artifact_id = generate_artifact_id(artifact_type, card_id)

        # Create artifact
        artifact = create_artifact(
            artifact_type=artifact_type,
            card_id=card_id,
            task_title=task_title,
            content=content,
            artifact_id=artifact_id,
            metadata=metadata
        )

        # Prepare metadata for storage
        chromadb_metadata = prepare_artifact_metadata(
            card_id=card_id,
            task_title=task_title,
            timestamp=artifact.timestamp,
            additional_metadata=metadata
        )

        # Store in vector store
        success = self.vector_store.add_artifact(artifact, chromadb_metadata)

        return artifact_id if success else None

    def query_similar(
        self,
        query_text: str,
        artifact_types: Optional[List[str]] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
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
        return self.retriever.query_similar(
            query_text=query_text,
            artifact_types=artifact_types,
            top_k=top_k,
            filters=filters
        )

    def get_recommendations(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get RAG-informed recommendations based on past experience.

        Args:
            task_description: Description of new task
            context: Additional context (technologies, priority, etc.)

        Returns:
            Dict with recommendations based on history
        """
        return self.pattern_analyzer.get_recommendations(
            task_description=task_description,
            context=context
        )

    def extract_patterns(
        self,
        pattern_type: str = "technology_success_rates",
        time_window_days: int = 90
    ) -> Dict[str, Any]:
        """
        Extract learning patterns from stored artifacts.

        Args:
            pattern_type: Type of pattern to extract
            time_window_days: Time window for analysis

        Returns:
            Dict with extracted patterns
        """
        return self.pattern_analyzer.extract_patterns(
            pattern_type=pattern_type,
            time_window_days=time_window_days
        )

    def search_code_examples(
        self,
        query: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for code examples in RAG database.

        Args:
            query: Code snippet or description to search for
            language: Filter by programming language
            framework: Filter by framework
            top_k: Number of results to return

        Returns:
            List of code examples with metadata
        """
        return self.retriever.search_code_examples(
            query=query,
            language=language,
            framework=framework,
            top_k=top_k
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG database statistics.

        Returns:
            Statistics dictionary
        """
        counts = self.vector_store.get_all_counts()
        total = sum(counts.values())

        return {
            "total_artifacts": total,
            "by_type": counts,
            "database_path": str(self.db_path),
            "chromadb_available": self.vector_store.chromadb_available
        }
