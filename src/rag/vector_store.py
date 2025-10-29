from artemis_logger import get_logger
logger = get_logger('vector_store')
'\nWHY: Abstract vector storage operations behind a clean interface.\n     Supports both ChromaDB (production) and mock storage (testing/fallback).\n\nRESPONSIBILITY:\n- Manage ChromaDB client lifecycle\n- Initialize and maintain collections per artifact type\n- Provide add/query operations on vector store\n- Handle fallback to mock storage when ChromaDB unavailable\n\nPATTERNS:\n- Repository Pattern: Abstract storage behind interface\n- Strategy Pattern: ChromaDB vs Mock storage strategies\n- Null Object Pattern: Mock storage for graceful degradation\n'
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import asdict
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
from rag.models import Artifact, ARTIFACT_TYPES

class VectorStore:
    """
    Vector storage abstraction supporting ChromaDB and mock storage.

    Provides consistent interface regardless of backend implementation.
    """

    def __init__(self, db_path: Path, log_fn: Optional[Callable[[str], None]]=None):
        """
        Initialize vector store.

        Args:
            db_path: Path to database directory
            log_fn: Optional logging function
        """
        self.db_path = db_path
        self.log_fn = log_fn or (lambda msg: None)
        self.chromadb_available = CHROMADB_AVAILABLE
        if not CHROMADB_AVAILABLE:
            
            logger.log('⚠️  ChromaDB not installed. RAG Agent will run in mock mode.', 'INFO')
            
            logger.log('   Install with: pip install chromadb sentence-transformers', 'INFO')
        if CHROMADB_AVAILABLE:
            self.client = chromadb.PersistentClient(path=str(db_path), settings=Settings(anonymized_telemetry=False))
            self.collections = self._initialize_collections()
            self.mock_storage = {}
        else:
            self.client = None
            self.collections = {}
            self.mock_storage = {}
        self.log_fn(f'Vector store initialized at {db_path}')

    def _initialize_collections(self) -> Dict[str, Any]:
        """
        Initialize ChromaDB collections for each artifact type.

        Returns:
            Dictionary mapping artifact types to collections
        """
        collections = {}
        for artifact_type in ARTIFACT_TYPES:
            collections[artifact_type] = self.client.get_or_create_collection(name=artifact_type, metadata={'description': f'Storage for {artifact_type} artifacts'})
        self.log_fn(f'Initialized {len(collections)} collections')
        return collections

    def add_artifact(self, artifact: Artifact, chromadb_metadata: Dict[str, Any]) -> bool:
        """
        Add artifact to vector store.

        Args:
            artifact: Artifact to store
            chromadb_metadata: Prepared metadata for ChromaDB

        Returns:
            True if successful, False otherwise
        """
        if artifact.artifact_type not in ARTIFACT_TYPES:
            self.log_fn(f'⚠️  Unknown artifact type: {artifact.artifact_type}')
            return False
        if self.chromadb_available and self.client:
            collection = self.collections[artifact.artifact_type]
            collection.add(ids=[artifact.artifact_id], documents=[artifact.content], metadatas=[chromadb_metadata])
            self.log_fn(f'✅ Stored {artifact.artifact_type}: {artifact.artifact_id}')
            return True
        if artifact.artifact_type not in self.mock_storage:
            self.mock_storage[artifact.artifact_type] = []
        self.mock_storage[artifact.artifact_type].append(asdict(artifact))
        self.log_fn(f'✅ Stored (mock) {artifact.artifact_type}: {artifact.artifact_id}')
        return True

    def query_collection(self, artifact_type: str, query_text: str, top_k: int=5, where: Optional[Dict[str, Any]]=None) -> Optional[Dict[str, Any]]:
        """
        Query a specific collection.

        Args:
            artifact_type: Type of artifact to query
            query_text: Query text for semantic search
            top_k: Number of results
            where: Optional metadata filters

        Returns:
            Query results or None if collection doesn't exist
        """
        if artifact_type not in self.collections:
            return None
        collection = self.collections[artifact_type]
        query_results = collection.query(query_texts=[query_text], n_results=min(top_k, 10), where=where)
        return query_results

    def mock_search(self, artifact_type: str, query_text: str) -> List[Dict[str, Any]]:
        """
        Simple keyword-based mock search.

        Args:
            artifact_type: Type of artifact to search
            query_text: Query text

        Returns:
            List of matching artifacts
        """
        if artifact_type not in self.mock_storage:
            return []
        query_lower = query_text.lower()
        results = []
        for artifact in self.mock_storage[artifact_type]:
            if query_lower in artifact['content'].lower():
                results.append({**artifact, 'similarity': 0.85})
        return results

    def get_collection_count(self, artifact_type: str) -> int:
        """
        Get count of artifacts in a collection.

        Args:
            artifact_type: Type of artifact

        Returns:
            Number of artifacts
        """
        if self.chromadb_available and artifact_type in self.collections:
            return self.collections[artifact_type].count()
        if artifact_type in self.mock_storage:
            return len(self.mock_storage[artifact_type])
        return 0

    def get_all_counts(self) -> Dict[str, int]:
        """
        Get counts for all artifact types.

        Returns:
            Dictionary mapping artifact types to counts
        """
        counts = {}
        if self.chromadb_available:
            for artifact_type, collection in self.collections.items():
                counts[artifact_type] = collection.count()
        else:
            for artifact_type, artifacts in self.mock_storage.items():
                counts[artifact_type] = len(artifacts)
        return counts