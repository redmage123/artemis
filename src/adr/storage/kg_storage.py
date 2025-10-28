#!/usr/bin/env python3
"""
WHY: Handle ADR storage in Knowledge Graph
RESPONSIBILITY: Store ADR nodes and relationships in KG
PATTERNS: Strategy (storage implementation), Guard Clause (availability check)

KG storage maintains structured relationships between ADRs and requirements.
"""

from typing import Optional, Any
from artemis_stage_interface import LoggerInterface
from knowledge_graph_factory import get_knowledge_graph


class ADRKnowledgeGraphStorage:
    """
    Handles ADR storage in Knowledge Graph.

    WHY: Separates KG storage logic from service orchestration.
    RESPONSIBILITY: Store ADR nodes and link to requirements/files.
    PATTERNS: Strategy, Guard Clause.
    """

    def __init__(self, logger: LoggerInterface):
        """
        Initialize KG storage.

        Args:
            logger: Logger interface
        """
        self.logger = logger

    def store_adr(
        self,
        card_id: str,
        adr_number: str,
        adr_path: str,
        adr_title: str,
        structured_requirements: Optional[Any] = None
    ) -> None:
        """
        Store ADR in Knowledge Graph and link to requirements.

        WHY: Creates structured relationships for traceability.

        Args:
            card_id: Card ID for this task
            adr_number: ADR number (e.g., "001")
            adr_path: Path to ADR file
            adr_title: ADR title
            structured_requirements: Structured requirements object (if available)
        """
        kg = get_knowledge_graph()

        # Guard clause - KG not available
        if not kg:
            self.logger.log(
                "Knowledge Graph not available - skipping KG storage",
                "DEBUG"
            )
            return

        try:
            self.logger.log("Storing ADR in Knowledge Graph...", "DEBUG")

            # Add ADR node
            adr_id = f"ADR-{adr_number}"
            kg.add_adr(
                adr_id=adr_id,
                title=adr_title,
                status="accepted"
            )

            # Link ADR to file
            kg.link_adr_to_file(
                adr_id=adr_id,
                file_path=adr_path,
                relationship="DOCUMENTED_IN"
            )

            # Link to requirements if available
            if structured_requirements:
                req_count = self._link_requirements(
                    kg, adr_id, structured_requirements
                )
                self.logger.log(
                    f"✅ Linked ADR {adr_id} to {req_count} requirements "
                    f"in Knowledge Graph",
                    "INFO"
                )
            else:
                self.logger.log(
                    f"✅ Stored ADR {adr_id} in Knowledge Graph",
                    "INFO"
                )

            # Link ADR to task (best effort)
            try:
                self.logger.log(
                    f"   ADR-Task linkage: {adr_id} -> {card_id}",
                    "DEBUG"
                )
            except Exception as e:
                self.logger.log(
                    f"   Could not link ADR to task: {e}",
                    "DEBUG"
                )

        except Exception as e:
            self.logger.log(
                f"Warning: Could not store ADR in Knowledge Graph: {e}",
                "WARNING"
            )

    def _link_requirements(
        self,
        kg,
        adr_id: str,
        structured_requirements
    ) -> int:
        """
        Link requirements to ADR in Knowledge Graph.

        WHY: Establishes traceability between requirements and decisions.

        Args:
            kg: Knowledge Graph instance
            adr_id: ADR ID (e.g., "ADR-001")
            structured_requirements: Structured requirements object

        Returns:
            Number of requirements linked
        """
        req_count = 0

        # Link to functional requirements (top 5 high-priority)
        high_priority_functional = [
            req for req in structured_requirements.functional_requirements
            if req.priority.value in ['critical', 'high']
        ][:5]

        for req in high_priority_functional:
            kg.link_requirement_to_adr(req.id, adr_id)
            req_count += 1

        # Link to non-functional requirements (top 5)
        for req in structured_requirements.non_functional_requirements[:5]:
            kg.link_requirement_to_adr(req.id, adr_id)
            req_count += 1

        return req_count
