#!/usr/bin/env python3
"""
WHY: Analyze project context from RAG to enrich ADR generation
RESPONSIBILITY: Query and extract Software Specification Document (SSD) context
PATTERNS: Guard clauses, generator patterns for lazy evaluation, single responsibility
"""

import json
from typing import Dict, List, Optional, Any, Generator

from artemis_stage_interface import LoggerInterface
from documentation.models import SSDContext


class ContextAnalyzer:
    """
    WHY: Query RAG for SSD artifacts and build comprehensive context
    RESPONSIBILITY: Extract and structure context from RAG queries
    PATTERNS: Guard clauses for early returns, generator patterns for processing
    """

    def __init__(self, rag, logger: LoggerInterface):
        """
        Initialize context analyzer

        Args:
            rag: RAG agent for querying context
            logger: Logger interface
        """
        self.rag = rag
        self.logger = logger

    def query_ssd_context(self, card_id: str) -> Optional[SSDContext]:
        """
        Query RAG for Software Specification Document artifacts

        Args:
            card_id: Card ID to query SSD for

        Returns:
            SSDContext or None if SSD not found/not generated
        """
        # Guard clause: Check RAG available
        if not self.rag:
            self.logger.log("⚠️  RAG not available for SSD context query", "WARNING")
            return None

        try:
            # Query RAG for different SSD artifact types
            executive_results = self._query_executive_summary(card_id)
            requirements_results = self._query_requirements(card_id)
            diagram_results = self._query_diagrams(card_id)

            # Guard clause: Check if SSD found
            if not executive_results:
                self.logger.log("No SSD found in RAG (task may have skipped SSD generation)", "INFO")
                return None

            # Build SSD context from results
            ssd_context = self._build_ssd_context(
                executive_results,
                requirements_results,
                diagram_results
            )

            self.logger.log(f"✅ Retrieved SSD from RAG for card {card_id}", "SUCCESS")
            self.logger.log(f"   Found {len(requirements_results)} requirements", "INFO")
            self.logger.log(f"   Found {len(diagram_results)} diagrams", "INFO")

            return ssd_context

        except Exception as e:
            self.logger.log(f"⚠️  Failed to query SSD from RAG: {e}", "WARNING")
            return None

    def _query_executive_summary(self, card_id: str) -> List[Dict[str, Any]]:
        """
        Query RAG for SSD executive summary

        Args:
            card_id: Card ID to query for

        Returns:
            List of executive summary results
        """
        return self.rag.query_similar(
            query_text=f"software specification document {card_id} executive summary business case",
            artifact_type="ssd_executive_summary",
            card_id=card_id,
            top_k=1
        )

    def _query_requirements(self, card_id: str) -> List[Dict[str, Any]]:
        """
        Query RAG for SSD requirements

        Args:
            card_id: Card ID to query for

        Returns:
            List of requirement results
        """
        return self.rag.query_similar(
            query_text=f"software specification {card_id} requirements functional non-functional",
            artifact_type="ssd_requirement",
            card_id=card_id,
            top_k=5
        )

    def _query_diagrams(self, card_id: str) -> List[Dict[str, Any]]:
        """
        Query RAG for SSD diagrams

        Args:
            card_id: Card ID to query for

        Returns:
            List of diagram results
        """
        return self.rag.query_similar(
            query_text=f"software specification {card_id} architecture diagram erd",
            artifact_type="ssd_diagram",
            card_id=card_id,
            top_k=3
        )

    def _build_ssd_context(
        self,
        executive_results: List[Dict[str, Any]],
        requirements_results: List[Dict[str, Any]],
        diagram_results: List[Dict[str, Any]]
    ) -> SSDContext:
        """
        Build SSD context from RAG query results

        Args:
            executive_results: Executive summary results
            requirements_results: Requirements results
            diagram_results: Diagram results

        Returns:
            SSDContext instance
        """
        # Extract executive content
        executive_content = next(
            (result.get('content', '') for result in executive_results),
            ''
        )

        # Split executive summary and business case
        executive_parts = executive_content.split('\n\n', 1)
        executive_summary = executive_parts[0] if executive_parts else executive_content
        business_case = executive_parts[1] if len(executive_parts) > 1 else ''

        # Extract key requirements using generator
        key_requirements = '\n'.join(self._extract_key_requirements(requirements_results))

        # Extract diagram descriptions using generator
        diagram_descriptions = '\n'.join(self._extract_diagram_descriptions(diagram_results))

        # Count functional and non-functional requirements
        functional_count = sum(
            1 for r in requirements_results
            if r.get('metadata', {}).get('category') == 'functional'
        )
        non_functional_count = sum(
            1 for r in requirements_results
            if r.get('metadata', {}).get('category') == 'non_functional'
        )

        # Extract constraints and success criteria
        constraints = self._extract_list_from_content(executive_content, "Constraints")
        success_criteria = self._extract_list_from_content(executive_content, "Success Criteria")

        return SSDContext(
            executive_summary=executive_summary,
            business_case=business_case,
            functional_count=functional_count,
            non_functional_count=non_functional_count,
            key_requirements=key_requirements if key_requirements else "No specific requirements found",
            diagram_descriptions=diagram_descriptions if diagram_descriptions else "No diagrams available",
            constraints=constraints,
            success_criteria=success_criteria
        )

    def _extract_key_requirements(
        self,
        requirements_results: List[Dict[str, Any]]
    ) -> Generator[str, None, None]:
        """
        Generator yielding formatted requirement strings

        Args:
            requirements_results: List of requirement results

        Yields:
            Formatted requirement string
        """
        for req_result in requirements_results[:5]:  # Top 5 requirements
            content = req_result.get('content', '')
            # Extract requirement ID and description from content
            lines = content.split('\n')

            # Guard clause: Skip if no lines
            if not lines:
                continue

            yield lines[0]  # First line usually has ID and description

    def _extract_diagram_descriptions(
        self,
        diagram_results: List[Dict[str, Any]]
    ) -> Generator[str, None, None]:
        """
        Generator yielding diagram descriptions

        Args:
            diagram_results: List of diagram results

        Yields:
            Formatted diagram description string
        """
        for diagram_result in diagram_results:
            content = diagram_result.get('content', '')

            # Guard clause: Try to parse JSON diagram data
            try:
                diagram_data = json.loads(content)
                diagram_type = diagram_data.get('type', 'diagram')
                description = diagram_data.get('description', 'No description')
                yield f"- {diagram_type}: {description}"
            except json.JSONDecodeError:
                continue

    def _extract_list_from_content(self, content: str, section_name: str) -> List[str]:
        """
        Extract list items from content section

        Args:
            content: Content to extract from
            section_name: Section name to find

        Returns:
            List of extracted items (max 5)
        """
        # Guard clause: Check content exists
        if not content or section_name not in content:
            return []

        # Find section
        section_start = content.find(section_name)
        if section_start == -1:
            return []

        # Get text after section header
        section_text = content[section_start:]

        # Extract bullet points using generator
        return list(self._extract_bullet_points(section_text))[:5]

    def _extract_bullet_points(self, section_text: str) -> Generator[str, None, None]:
        """
        Generator yielding bullet point items

        Args:
            section_text: Text to extract bullets from

        Yields:
            Cleaned bullet point text
        """
        for line in section_text.split('\n'):
            line = line.strip()

            # Guard clause: Skip if not a bullet point
            if not (line.startswith('-') or line.startswith('*')):
                continue

            yield line[1:].strip()


def create_context_analyzer(rag, logger: LoggerInterface) -> ContextAnalyzer:
    """
    Factory function to create ContextAnalyzer instance

    Args:
        rag: RAG agent
        logger: Logger interface

    Returns:
        ContextAnalyzer instance
    """
    return ContextAnalyzer(rag, logger)
