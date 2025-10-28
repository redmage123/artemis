#!/usr/bin/env python3
"""
WHY: Orchestrate semantic search across artifact collections.
     Provides unified interface for querying multiple artifact types.

RESPONSIBILITY:
- Execute queries across single or multiple artifact types
- Aggregate and rank results by similarity
- Apply metadata filters to search results
- Format raw results into SearchResult objects

PATTERNS:
- Facade Pattern: Simplify complex multi-collection queries
- Strategy Pattern: Different retrieval strategies (semantic vs keyword)
- Builder Pattern: Construct complex queries incrementally
"""

from typing import List, Dict, Optional, Any, Callable
from rag.models import SearchResult, create_search_result, ARTIFACT_TYPES
from rag.document_processor import deserialize_metadata
from rag.vector_store import VectorStore


class Retriever:
    """
    Handles semantic search and retrieval across artifact collections.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        log_fn: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize retriever.

        Args:
            vector_store: Vector store instance
            log_fn: Optional logging function
        """
        self.vector_store = vector_store
        self.log_fn = log_fn or (lambda msg: None)

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
            List of similar artifacts sorted by similarity
        """
        # Guard: Default to all artifact types
        if artifact_types is None:
            artifact_types = ARTIFACT_TYPES

        results = []

        # Execute search strategy
        if self.vector_store.chromadb_available:
            results = self._semantic_search(query_text, artifact_types, top_k, filters)
        else:
            results = self._keyword_search(query_text, artifact_types)

        # Sort and limit results
        results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        results = results[:top_k]

        self.log_fn(f"🔍 Found {len(results)} similar artifacts for: {query_text[:50]}...")
        return results

    def _semantic_search(
        self,
        query_text: str,
        artifact_types: List[str],
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute semantic search using ChromaDB.

        Args:
            query_text: Query text
            artifact_types: Types to search
            top_k: Number of results per type
            filters: Metadata filters

        Returns:
            List of search results
        """
        results = []

        for artifact_type in artifact_types:
            # Query collection
            query_results = self.vector_store.query_collection(
                artifact_type=artifact_type,
                query_text=query_text,
                top_k=top_k,
                where=filters
            )

            # Guard: Skip if no results
            if not query_results or not query_results.get('ids'):
                continue

            # Process results
            for i, artifact_id in enumerate(query_results['ids'][0]):
                metadata = deserialize_metadata(query_results['metadatas'][0][i])

                results.append({
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "content": query_results['documents'][0][i],
                    "metadata": metadata,
                    "distance": query_results['distances'][0][i] if 'distances' in query_results else None,
                    "similarity": 1.0 - query_results['distances'][0][i] if 'distances' in query_results else 1.0
                })

        return results

    def _keyword_search(
        self,
        query_text: str,
        artifact_types: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Execute simple keyword-based search (mock).

        Args:
            query_text: Query text
            artifact_types: Types to search

        Returns:
            List of search results
        """
        results = []

        for artifact_type in artifact_types:
            mock_results = self.vector_store.mock_search(artifact_type, query_text)
            results.extend(mock_results)

        return results

    def search_code_examples(
        self,
        query: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for code examples with optional filtering.

        Args:
            query: Code snippet or description
            language: Filter by programming language
            framework: Filter by framework
            top_k: Number of results

        Returns:
            List of formatted code examples
        """
        # Build filters
        filters = {}
        if language:
            filters['language'] = language
        if framework:
            filters['framework'] = framework

        # Query code_example artifacts
        results = self.query_similar(
            query_text=query,
            artifact_types=['code_example'],
            top_k=top_k,
            filters=filters if filters else None
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'code': result.get('content', ''),
                'source': result.get('metadata', {}).get('source', 'unknown'),
                'language': result.get('metadata', {}).get('language', language or 'python'),
                'framework': result.get('metadata', {}).get('framework'),
                'metadata': result.get('metadata', {}),
                'score': result.get('similarity', 0.0)
            })

        return formatted_results
