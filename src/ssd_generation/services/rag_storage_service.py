#!/usr/bin/env python3
"""
RAG Storage Service

WHY: Stores SSD artifacts in RAG for architecture agent retrieval.
RESPONSIBILITY: Store SSD content in RAG with proper metadata.
PATTERNS:
- Guard clauses (Pattern #10)
- Generator pattern (Pattern #11) for batch processing
- Single Responsibility
"""

import json
from typing import Optional, Generator, Tuple

from artemis_stage_interface import LoggerInterface
from rag_agent import RAGAgent
from ssd_generation.models.ssd_document import SSDDocument


class RAGStorageService:
    """
    Stores SSD artifacts in RAG for architecture agent

    WHY: Enables architecture agent to access SSD content during design phase.
    WHEN: Called after SSD generation to persist content to RAG.
    """

    def __init__(
        self,
        rag: RAGAgent,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True
    ):
        """Initialize RAG storage service"""
        self.rag = rag
        self.logger = logger
        self.verbose = verbose

    def store_ssd(self, card_id: str, ssd_document: SSDDocument) -> None:
        """
        Store SSD in RAG for architecture agent retrieval

        Pattern #10: Guard clauses
        Pattern #11: Generator for batch processing
        """
        # Guard clause: Check RAG available
        if not self.rag:
            return

        if self.verbose and self.logger:
            self.logger.log("💾 Storing SSD in RAG...", "INFO")

        # Store executive summary
        self._store_executive_summary(card_id, ssd_document)

        # Store requirements
        self._store_requirements(card_id, ssd_document)

        # Store diagram specifications
        self._store_diagrams(card_id, ssd_document)

        if self.verbose and self.logger:
            self.logger.log("   SSD stored in RAG", "SUCCESS")

    def _store_executive_summary(
        self,
        card_id: str,
        ssd_document: SSDDocument
    ) -> None:
        """Store executive summary in RAG"""
        self.rag.store_artifact(
            artifact_type="ssd_executive_summary",
            card_id=card_id,
            task_title=ssd_document.project_name,
            content=f"{ssd_document.executive_summary}\n\n{ssd_document.business_case}",
            metadata={"section": "executive"}
        )

    def _store_requirements(
        self,
        card_id: str,
        ssd_document: SSDDocument
    ) -> None:
        """
        Store requirements in RAG

        Pattern #11: Generator for storing requirement batches
        """
        def _generate_requirements() -> Generator[Tuple[str, str, str], None, None]:
            """Generator for storing requirement batches"""
            all_requirements = (
                ssd_document.functional_requirements +
                ssd_document.non_functional_requirements +
                ssd_document.business_requirements
            )

            for req in all_requirements:
                content = f"""
# {req.id}: {req.description}

**Category**: {req.category}
**Priority**: {req.priority}

## Acceptance Criteria
{chr(10).join(f"- {criterion}" for criterion in req.acceptance_criteria)}

## Dependencies
{chr(10).join(f"- {dep}" for dep in req.dependencies) if req.dependencies else "None"}
"""
                yield (req.id, content, req.category)

        # Store requirements (using generator)
        for req_id, content, category in _generate_requirements():
            self.rag.store_artifact(
                artifact_type="ssd_requirement",
                card_id=card_id,
                task_title=f"Requirement {req_id}",
                content=content,
                metadata={"requirement_id": req_id, "category": category}
            )

    def _store_diagrams(
        self,
        card_id: str,
        ssd_document: SSDDocument
    ) -> None:
        """Store diagram specifications in RAG"""
        for diagram in ssd_document.diagrams:
            self.rag.store_artifact(
                artifact_type="ssd_diagram",
                card_id=card_id,
                task_title=diagram.title,
                content=json.dumps({
                    "type": diagram.diagram_type,
                    "description": diagram.description,
                    "chart_js_config": diagram.chart_js_config,
                    "mermaid_syntax": diagram.mermaid_syntax
                }, indent=2),
                metadata={"diagram_type": diagram.diagram_type}
            )
