#!/usr/bin/env python3
"""
WHY: Handle example storage operations
RESPONSIBILITY: Store examples in RAG with metadata
PATTERNS: Strategy (storage operations)

Storage module provides RAG persistence for research examples.
"""

from typing import List
from rag_agent import RAGAgent
from research.models import ResearchExample
from research_exceptions import ExampleStorageError


class ExampleStorage:
    """
    Handles storage of research examples in RAG.

    WHY: Separates storage logic from repository interface.
    RESPONSIBILITY: Persist examples with metadata to RAG.
    PATTERNS: Strategy (pluggable storage).
    """

    ARTIFACT_TYPE = "code_example"

    def __init__(self, rag_agent: RAGAgent):
        """
        Initialize storage.

        Args:
            rag_agent: RAG agent for persistence
        """
        self.rag = rag_agent

    def store_single(
        self,
        example: ResearchExample,
        card_id: str,
        task_title: str
    ) -> str:
        """
        Store a single research example in RAG.

        WHY: Atomic storage operation with error handling.

        Args:
            example: Research example to store
            card_id: Card ID for tracking
            task_title: Task title

        Returns:
            Artifact ID

        Raises:
            ExampleStorageError: If storage fails
        """
        try:
            # Prepare metadata
            metadata = {
                "source": example.source,
                "url": example.url or "",
                "language": example.language,
                "tags": example.tags,
                "relevance_score": example.relevance_score,
                "example_type": "research"
            }

            # Store in RAG
            artifact_id = self.rag.store_artifact(
                artifact_type=self.ARTIFACT_TYPE,
                card_id=card_id,
                task_title=f"{task_title} - {example.title}",
                content=example.content,
                metadata=metadata
            )

            return artifact_id

        except Exception as e:
            raise ExampleStorageError(
                artifact_id=example.title,
                message=f"Failed to store example '{example.title}'",
                cause=e
            )

    def store_batch(
        self,
        examples: List[ResearchExample],
        card_id: str,
        task_title: str,
        error_threshold: float = 0.5
    ) -> List[str]:
        """
        Store multiple examples in batch.

        WHY: Batch operations with partial failure tolerance.

        Args:
            examples: List of research examples
            card_id: Card ID
            task_title: Task title
            error_threshold: Max ratio of failures before raising (default 50%)

        Returns:
            List of artifact IDs

        Raises:
            ExampleStorageError: If error rate exceeds threshold
        """
        artifact_ids = []
        errors = []

        for example in examples:
            try:
                artifact_id = self.store_single(example, card_id, task_title)
                artifact_ids.append(artifact_id)
            except ExampleStorageError as e:
                errors.append(str(e))

        # Guard clause - raise if too many errors
        if len(errors) > len(examples) * error_threshold:
            raise ExampleStorageError(
                artifact_id="batch",
                message=f"Failed to store {len(errors)}/{len(examples)} examples",
                cause=Exception("; ".join(errors))
            )

        return artifact_ids
