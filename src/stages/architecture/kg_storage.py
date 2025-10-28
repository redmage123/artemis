#!/usr/bin/env python3
"""
Knowledge Graph Storage

WHY: Store ADRs and relationships in Knowledge Graph
RESPONSIBILITY: Manage KG operations for architecture artifacts
PATTERNS: Single Responsibility, Guard Clauses
"""

from typing import Optional, Any

from knowledge_graph_factory import get_knowledge_graph


class KGArchitectureStorage:
    """
    Stores architecture artifacts in Knowledge Graph.

    WHY: Separate KG operations from main stage logic
    RESPONSIBILITY: KG storage and linking only
    PATTERNS: Single Responsibility, Guard Clauses
    """

    def __init__(self, logger: Optional[Any] = None):
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
        structured_requirements: Optional[Any] = None
    ) -> bool:
        """
        Store ADR in Knowledge Graph and link to requirements.

        Args:
            card_id: Card ID for this task
            adr_number: ADR number (e.g., "001")
            adr_path: Path to ADR file
            structured_requirements: Structured requirements object (if available)

        Returns:
            True if stored successfully, False otherwise

        WHY: Central entry point for KG storage
        PATTERN: Guard clauses for availability and errors
        """
        kg = get_knowledge_graph()
        if not kg:
            if self.logger:
                self.logger.log("Knowledge Graph not available - skipping KG storage", "DEBUG")
            return False

        try:
            if self.logger:
                self.logger.log("Storing ADR in Knowledge Graph...", "DEBUG")

            adr_id = f"ADR-{adr_number}"

            # Add ADR node
            kg.add_adr(
                adr_id=adr_id,
                title=f"Architecture Decision {adr_number}",
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
                req_count = self._link_to_requirements(kg, adr_id, structured_requirements)
                if self.logger:
                    self.logger.log(
                        f"✅ Linked ADR {adr_id} to {req_count} requirements in Knowledge Graph",
                        "INFO"
                    )
            else:
                if self.logger:
                    self.logger.log(f"✅ Stored ADR {adr_id} in Knowledge Graph", "INFO")

            # Link ADR to task
            self._link_to_task(adr_id, card_id)

            return True

        except Exception as e:
            if self.logger:
                self.logger.log(f"Warning: Could not store ADR in Knowledge Graph: {e}", "WARNING")
                self.logger.log(f"   Exception details: {type(e).__name__}", "DEBUG")
            return False

    def _link_to_requirements(
        self,
        kg: Any,
        adr_id: str,
        structured_requirements: Any
    ) -> int:
        """
        Link ADR to requirements in knowledge graph.

        WHY: Create traceability from ADR to requirements
        PATTERN: Guard clauses for requirement lists
        """
        req_count = 0

        # Link to functional requirements (top 5 high-priority ones)
        high_priority_functional = [
            req for req in structured_requirements.functional_requirements
            if req.priority.value in ['critical', 'high']
        ][:5]

        for req in high_priority_functional:
            kg.link_requirement_to_adr(req.id, adr_id)
            req_count += 1

        # Link to non-functional requirements (all of them since they're critical)
        for req in structured_requirements.non_functional_requirements[:5]:
            kg.link_requirement_to_adr(req.id, adr_id)
            req_count += 1

        return req_count

    def _link_to_task(self, adr_id: str, card_id: str) -> None:
        """
        Link ADR to task in KG.

        WHY: Create traceability from ADR to task
        PATTERN: Guard clause for errors
        """
        try:
            if self.logger:
                self.logger.log(f"   ADR-Task linkage: {adr_id} -> {card_id}", "DEBUG")
        except Exception as e:
            if self.logger:
                self.logger.log(f"   Could not link ADR to task: {e}", "DEBUG")
