#!/usr/bin/env python3
"""
WHY: Define core data structures for RAG system artifacts and search results.
     Provides immutable, type-safe models for document storage and retrieval.

RESPONSIBILITY:
- Define Artifact structure for pipeline memory
- Define SearchResult structure for query responses
- Provide serialization/deserialization for persistence

PATTERNS:
- Dataclass Pattern: Immutable data containers with type hints
- Value Object Pattern: Artifacts represent immutable domain objects
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Artifact:
    """
    Pipeline artifact for storage.

    Represents a single unit of knowledge stored in the RAG system.
    Immutable once created to ensure data integrity.
    """
    artifact_id: str
    artifact_type: str  # research_report, adr, solution, validation, etc.
    card_id: str
    task_title: str
    content: str
    metadata: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary for serialization."""
        return asdict(self)


@dataclass
class SearchResult:
    """
    Result from similarity search query.

    Contains matched artifact with similarity score and metadata.
    """
    artifact_id: str
    artifact_type: str
    content: str
    metadata: Dict[str, Any]
    similarity: float
    distance: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary."""
        return asdict(self)


# Artifact type constants
ARTIFACT_TYPES: List[str] = [
    "research_report",
    "project_analysis",
    "project_review",        # Project review stage quality gate
    "architecture_decision",
    "developer_solution",
    "validation_result",
    "arbitration_score",
    "integration_result",
    "testing_result",
    "issue_and_fix",
    "issue_resolution",      # Supervisor issue resolution tracking
    "supervisor_recovery",   # Supervisor recovery workflow outcomes
    "sprint_plan",           # Sprint planning with story point estimates
    "notebook_example",      # Jupyter notebook examples for demonstrations
    "code_example"           # Code examples from research stage (GitHub, HuggingFace, local)
]


def create_artifact(
    artifact_type: str,
    card_id: str,
    task_title: str,
    content: str,
    artifact_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Artifact:
    """
    Factory function to create an Artifact with current timestamp.

    Args:
        artifact_type: Type of artifact
        card_id: Card identifier
        task_title: Task title
        content: Full content text
        artifact_id: Unique artifact identifier
        metadata: Additional metadata (optional)

    Returns:
        Initialized Artifact instance
    """
    return Artifact(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        card_id=card_id,
        task_title=task_title,
        content=content,
        metadata=metadata or {},
        timestamp=datetime.utcnow().isoformat() + 'Z'
    )


def create_search_result(
    artifact_id: str,
    artifact_type: str,
    content: str,
    metadata: Dict[str, Any],
    similarity: float,
    distance: Optional[float] = None
) -> SearchResult:
    """
    Factory function to create a SearchResult.

    Args:
        artifact_id: Unique artifact identifier
        artifact_type: Type of artifact
        content: Full content text
        metadata: Artifact metadata
        similarity: Similarity score (0.0 to 1.0)
        distance: Optional distance metric

    Returns:
        Initialized SearchResult instance
    """
    return SearchResult(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        content=content,
        metadata=metadata,
        similarity=similarity,
        distance=distance
    )
