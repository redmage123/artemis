#!/usr/bin/env python3
"""
Requirements Analyzer Service

WHY: Analyzes card content to extract and structure requirements.
RESPONSIBILITY: Transform raw card data into structured requirements.
PATTERNS:
- Guard clauses (Pattern #10)
- Generator pattern (Pattern #11) for large datasets
- Single Responsibility Principle
"""

import json
from typing import Dict, List, Any, Optional

from artemis_exceptions import PipelineStageError
from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient
from ssd_generation.models.requirement_item import RequirementItem
from ssd_generation.prompts.requirements_prompts import RequirementsPrompts


class RequirementsAnalyzer:
    """
    Analyzes and extracts structured requirements from task cards

    WHY: Converts unstructured task descriptions into structured requirements.
    WHEN: Called during SSD generation to extract requirements.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        logger: Optional[LoggerInterface] = None,
        verbose: bool = True
    ):
        """Initialize requirements analyzer"""
        self.llm_client = llm_client
        self.logger = logger
        self.verbose = verbose
        self.prompts = RequirementsPrompts()

    def analyze_requirements(
        self,
        card: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze card to extract high-level requirements

        Pattern #10: Guard clauses for validation
        """
        # Guard clause: Check for description
        if not card.get('description') and not card.get('title'):
            raise PipelineStageError(
                "SSD Generation",
                "Card must have description or title"
            )

        task_description = card.get('description', card.get('title', ''))
        task_title = card.get('title', 'Untitled')

        if self.verbose and self.logger:
            self.logger.log("🔍 Analyzing Requirements...", "INFO")

        # Build analysis prompt
        prompt = self.prompts.build_requirements_analysis_prompt(
            task_title,
            task_description,
            context
        )

        # Query LLM for requirements analysis
        response = self.llm_client.query(prompt)

        # Parse response (expect JSON)
        analysis = self._parse_json_response(response)

        if self.verbose and self.logger:
            self.logger.log(
                f"   Found {len(analysis.get('key_features', []))} key features",
                "INFO"
            )

        return analysis

    def generate_executive_summary(
        self,
        card: Dict[str, Any],
        requirements_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate executive summary and business case"""
        if self.verbose and self.logger:
            self.logger.log("📝 Generating Executive Summary...", "INFO")

        prompt = self.prompts.build_executive_summary_prompt(card, requirements_analysis)
        response = self.llm_client.query(prompt)

        # Parse response
        content = self._parse_json_response(response)

        return {
            "executive_summary": content.get('executive_summary', ''),
            "business_case": content.get('business_case', '')
        }

    def extract_requirements(
        self,
        card: Dict[str, Any],
        requirements_analysis: Dict[str, Any]
    ) -> Dict[str, List[RequirementItem]]:
        """
        Extract structured requirements (functional, non-functional, business)

        Pattern #11: Generator pattern for processing large requirement lists
        """
        if self.verbose and self.logger:
            self.logger.log("📋 Extracting Structured Requirements...", "INFO")

        prompt = self.prompts.build_requirements_extraction_prompt(
            card,
            requirements_analysis
        )

        response = self.llm_client.query(prompt)
        parsed = self._parse_json_response(response)

        # Pattern #11: Use generator to process requirements
        def _create_requirement_items(requirements_list: List[Dict], category: str):
            """Generator yielding RequirementItem objects"""
            for idx, req in enumerate(requirements_list, 1):
                yield RequirementItem(
                    id=f"{category.upper()}-{idx:03d}",
                    category=category,
                    priority=req.get('priority', 'should_have'),
                    description=req.get('description', ''),
                    acceptance_criteria=req.get('acceptance_criteria', []),
                    dependencies=req.get('dependencies', [])
                )

        # Convert generators to lists
        return {
            "functional": list(_create_requirement_items(
                parsed.get('functional_requirements', []),
                'functional'
            )),
            "non_functional": list(_create_requirement_items(
                parsed.get('non_functional_requirements', []),
                'non_functional'
            )),
            "business": list(_create_requirement_items(
                parsed.get('business_requirements', []),
                'business'
            ))
        }

    def generate_additional_sections(
        self,
        card: Dict[str, Any],
        requirements_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate constraints, assumptions, risks, success criteria"""
        if self.verbose and self.logger:
            self.logger.log("📊 Generating Additional Sections...", "INFO")

        prompt = self.prompts.build_additional_sections_prompt(card, requirements_analysis)
        response = self.llm_client.query(prompt)
        parsed = self._parse_json_response(response)

        return {
            "constraints": parsed.get('constraints', []),
            "assumptions": parsed.get('assumptions', []),
            "risks": parsed.get('risks', []),
            "success_criteria": parsed.get('success_criteria', [])
        }

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
