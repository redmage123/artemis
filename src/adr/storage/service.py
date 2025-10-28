#!/usr/bin/env python3
"""
WHY: Orchestrate ADR storage across multiple systems
RESPONSIBILITY: Coordinate RAG and KG storage operations
PATTERNS: Facade (unified interface), Composition (delegate to strategies)

Service provides single entry point for all ADR storage operations.
"""

from typing import List, Optional, Any
from artemis_stage_interface import LoggerInterface
from adr.storage.rag_storage import ADRRagStorage
from adr.storage.kg_storage import ADRKnowledgeGraphStorage


class ADRStorageService:
    """
    Service for storing ADR artifacts in storage systems.

    WHY: Single Responsibility - ADR artifact storage only.
    RESPONSIBILITY: Coordinate RAG and KG storage operations.
    PATTERNS: Facade, Composition, Strategy.

    Stores ADR content in:
    - RAG database for semantic search
    - Knowledge Graph for relationship tracking
    - Kanban board snapshots in RAG
    """

    def __init__(
        self,
        rag,  # RAGAgent
        board,  # KanbanBoard
        logger: LoggerInterface
    ):
        """
        Initialize ADR storage service.

        WHY: Composition - delegate to specialized storage strategies.

        Args:
            rag: RAG agent for artifact storage
            board: Kanban board for state queries
            logger: Logger interface
        """
        self.board = board
        self.logger = logger

        # Composition - delegate to storage strategies
        self.rag_storage = ADRRagStorage(rag, logger)
        self.kg_storage = ADRKnowledgeGraphStorage(logger)

    def store_adr_in_rag(
        self,
        card_id: str,
        task_title: str,
        adr_content: str,
        adr_number: str,
        adr_path: str,
        priority: str = "medium",
        story_points: int = 5
    ) -> None:
        """
        Store ADR content in RAG database.

        WHY: Delegates to RAG storage strategy.

        Args:
            card_id: Card ID for this task
            task_title: Task title
            adr_content: Full ADR content
            adr_number: ADR number (e.g., "001")
            adr_path: Path to ADR file
            priority: Task priority
            story_points: Story points
        """
        self.rag_storage.store_adr(
            card_id=card_id,
            task_title=task_title,
            adr_content=adr_content,
            adr_number=adr_number,
            adr_path=adr_path,
            priority=priority,
            story_points=story_points
        )

    def store_adr_in_knowledge_graph(
        self,
        card_id: str,
        adr_number: str,
        adr_path: str,
        adr_title: str,
        structured_requirements: Optional[Any] = None
    ) -> None:
        """
        Store ADR in Knowledge Graph and link to requirements.

        WHY: Delegates to KG storage strategy.

        Args:
            card_id: Card ID for this task
            adr_number: ADR number (e.g., "001")
            adr_path: Path to ADR file
            adr_title: ADR title
            structured_requirements: Structured requirements object (if available)
        """
        self.kg_storage.store_adr(
            card_id=card_id,
            adr_number=adr_number,
            adr_path=adr_path,
            adr_title=adr_title,
            structured_requirements=structured_requirements
        )

    def store_kanban_in_rag(
        self,
        card_id: str,
        story_card_ids: List[str]
    ) -> None:
        """
        Store Kanban board state in RAG database.

        WHY: Delegates to RAG storage strategy.

        Args:
            card_id: Parent card ID
            story_card_ids: List of generated story card IDs
        """
        self.rag_storage.store_kanban_state(
            card_id=card_id,
            story_card_ids=story_card_ids,
            board=self.board
        )
