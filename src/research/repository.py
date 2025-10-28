#!/usr/bin/env python3
"""
WHY: Implement Repository Pattern for research examples
RESPONSIBILITY: Provide clean interface abstracting RAG storage
PATTERNS: Repository (data access abstraction), Facade (unified interface)

Repository provides unified interface for research example management.
"""

from typing import List, Dict, Any, Optional
from rag_agent import RAGAgent
from research.models import ResearchExample
from research.storage import ExampleStorage
from research.query import ExampleQuery
from research.deduplicator import ExampleDeduplicator
from research.ranker import ExampleRanker


class ExampleRepository:
    """
    Repository Pattern for research examples.

    WHY: Abstracts RAG storage behind clean interface (DIP).
    RESPONSIBILITY: Coordinate storage, query, ranking, deduplication.
    PATTERNS: Repository, Facade, Composition.

    Provides a clean interface for storing and retrieving research examples.
    """

    def __init__(self, rag_agent: RAGAgent):
        """
        Initialize repository with RAG agent.

        Args:
            rag_agent: RAG agent for storage
        """
        # Composition: delegate to specialized components
        self.storage = ExampleStorage(rag_agent)
        self.query = ExampleQuery(rag_agent)

    def store_example(
        self,
        example: ResearchExample,
        card_id: str,
        task_title: str
    ) -> str:
        """
        Store a research example in RAG.

        WHY: Delegates to storage component (SRP).

        Args:
            example: Research example to store
            card_id: Card ID for tracking
            task_title: Task title

        Returns:
            Artifact ID

        Raises:
            ExampleStorageError: If storage fails
        """
        return self.storage.store_single(example, card_id, task_title)

    def store_examples_batch(
        self,
        examples: List[ResearchExample],
        card_id: str,
        task_title: str
    ) -> List[str]:
        """
        Store multiple examples in batch.

        WHY: Delegates to storage component with batch support.

        Args:
            examples: List of research examples
            card_id: Card ID
            task_title: Task title

        Returns:
            List of artifact IDs

        Raises:
            ExampleStorageError: If too many failures
        """
        return self.storage.store_batch(examples, card_id, task_title)

    def query_similar_examples(
        self,
        query: str,
        top_k: int = 5,
        language_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query for similar examples.

        WHY: Delegates to query component.

        Args:
            query: Search query
            top_k: Number of results
            language_filter: Optional language filter

        Returns:
            List of similar examples with metadata
        """
        return self.query.find_similar(query, top_k, language_filter)

    def get_example_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored examples.

        WHY: Delegates to query component for stats.

        Returns:
            Dictionary with statistics
        """
        return self.query.get_stats()

    def deduplicate_examples(
        self,
        examples: List[ResearchExample]
    ) -> List[ResearchExample]:
        """
        Remove duplicate examples based on content similarity.

        WHY: Delegates to deduplicator (SRP).

        Args:
            examples: List of research examples

        Returns:
            Deduplicated list
        """
        return ExampleDeduplicator.deduplicate(examples)

    def rank_examples_by_relevance(
        self,
        examples: List[ResearchExample],
        query: str,
        technologies: List[str]
    ) -> List[ResearchExample]:
        """
        Rank examples by relevance to query and technologies.

        WHY: Delegates to ranker (SRP).

        Args:
            examples: List of examples to rank
            query: Search query
            technologies: Technologies list

        Returns:
            Sorted list by relevance score
        """
        return ExampleRanker.rank_by_relevance(examples, query, technologies)
