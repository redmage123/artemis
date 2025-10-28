#!/usr/bin/env python3
"""
Diagram Generator Service

WHY: Generates diagram specifications for SSD documentation.
RESPONSIBILITY: Create architecture, ERD, and component diagrams.
PATTERNS:
- Generator pattern (Pattern #11) for large datasets
- Single Responsibility
"""

import json
from typing import Dict, List, Any, Optional

from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient
from ssd_generation.models.diagram_spec import DiagramSpec
from ssd_generation.models.requirement_item import RequirementItem
from ssd_generation.prompts.diagram_prompts import DiagramPrompts


class DiagramGenerator:
    """
    Generates diagram specifications for Chart.js and Mermaid

    WHY: Creates visual representations of system architecture and data models.
    WHEN: Called during SSD generation to produce diagram specs.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True
    ):
        """Initialize diagram generator"""
        self.llm_client = llm_client
        self.logger = logger
        self.verbose = verbose
        self.prompts = DiagramPrompts()

    def generate_diagram_specifications(
        self,
        card: Dict[str, Any],
        requirements: Dict[str, List[RequirementItem]],
        context: Dict[str, Any]
    ) -> List[DiagramSpec]:
        """
        Generate diagram specifications for Chart.js and Mermaid

        Includes:
        - Architecture diagrams
        - ERD with Crow's foot notation
        - Object-relational diagrams
        - Component diagrams
        """
        if self.verbose and self.logger:
            self.logger.log("🎨 Generating Diagram Specifications...", "INFO")

        prompt = self.prompts.build_diagram_generation_prompt(card, requirements, context)
        response = self.llm_client.query(prompt)
        parsed = self._parse_json_response(response)

        # Pattern #11: Generator for creating DiagramSpec objects
        def _create_diagram_specs():
            """Generator yielding DiagramSpec objects"""
            for diagram_data in parsed.get('diagrams', []):
                yield DiagramSpec(
                    diagram_type=diagram_data.get('type', 'architecture'),
                    title=diagram_data.get('title', ''),
                    description=diagram_data.get('description', ''),
                    chart_js_config=diagram_data.get('chart_js_config', {}),
                    mermaid_syntax=diagram_data.get('mermaid_syntax')
                )

        diagrams = list(_create_diagram_specs())

        if self.verbose and self.logger:
            self.logger.log(f"   Generated {len(diagrams)} diagram specifications", "INFO")

        return diagrams

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM

        Pattern #10: Guard clauses for error handling
        """
        # Guard clause: Check empty response
        if not response or not response.strip():
            return {}

        try:
            # Try to find JSON in response (may be wrapped in markdown code blocks)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            # Guard clause: Check JSON markers found
            if json_start == -1 or json_end == 0:
                return {}

            json_str = response[json_start:json_end]
            return json.loads(json_str)

        except json.JSONDecodeError:
            # Fallback: Return empty dict if parsing fails
            if self.verbose and self.logger:
                self.logger.log("⚠️  Failed to parse JSON response", "WARNING")
            return {}
