#!/usr/bin/env python3
"""
Requirements Conversion Utilities

WHY: Convert between different requirement representations
RESPONSIBILITY: Map LLM output format to StructuredRequirements dataclass
PATTERNS: Adapter pattern - adapts LLM format to our domain model
"""

from typing import Dict, Any, List
from datetime import datetime

from requirements_models import (
    StructuredRequirements,
    FunctionalRequirement,
    NonFunctionalRequirement,
    Stakeholder,
    Constraint,
    Assumption,
    Priority,
    RequirementType
)


class RequirementsConverter:
    """
    Convert LLM output to StructuredRequirements

    WHY: LLM outputs simpler format than our rich domain model
    RESPONSIBILITY: Bridge the gap between LLM and domain model
    PATTERNS: Adapter pattern
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize converter

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose

    def convert_llm_output_to_structured_requirements(
        self,
        llm_output: Dict[str, Any],
        project_name: str
    ) -> StructuredRequirements:
        """
        Convert LLM JSON output to StructuredRequirements object

        WHY: Separate conversion logic from main parser
        RESPONSIBILITY: Map flat LLM structure to rich dataclass model

        Args:
            llm_output: LLM JSON output with simpler structure
            project_name: Project name for metadata

        Returns:
            StructuredRequirements object
        """
        # Extract non-functional requirements
        nfr_data = llm_output.get("non_functional_requirements", {})

        # Convert functional requirements (strings → FunctionalRequirement objects)
        functional_reqs = self._convert_functional_requirements(llm_output)

        # Convert non-functional requirements
        non_functional_reqs = self._convert_non_functional_requirements(nfr_data)

        # Convert actors to stakeholders
        stakeholders = self._convert_actors_to_stakeholders(llm_output)

        # Convert risks to constraints (simplified mapping)
        constraints = self._convert_risks_to_constraints(llm_output)

        # Extract assumptions
        assumptions = self._convert_assumptions(llm_output)

        # Build structured requirements
        return StructuredRequirements(
            project_name=project_name,
            version="1.0",
            created_date=datetime.now().strftime("%Y-%m-%d"),
            executive_summary=llm_output.get("domain_context"),
            business_goals=llm_output.get("objectives", []),
            success_criteria=llm_output.get("acceptance_criteria", []),
            stakeholders=stakeholders,
            constraints=constraints,
            assumptions=assumptions,
            functional_requirements=functional_reqs,
            non_functional_requirements=non_functional_reqs,
            use_cases=[],  # TODO: Convert from LLM output if needed
            data_requirements=[],  # TODO: Convert from data_entities
            integration_requirements=[]  # TODO: Convert from integrations
        )

    def _convert_functional_requirements(
        self,
        llm_output: Dict[str, Any]
    ) -> List[FunctionalRequirement]:
        """
        Convert functional requirements from LLM output

        WHY: LLM outputs simple strings, we need rich objects
        RESPONSIBILITY: Create FunctionalRequirement objects from strings
        """
        functional_reqs = []
        for idx, req_text in enumerate(llm_output.get("functional_requirements", []), 1):
            functional_reqs.append(FunctionalRequirement(
                id=f"REQ-F-{idx:03d}",
                title=req_text[:100],  # First 100 chars as title
                description=req_text,
                priority=Priority.MEDIUM,  # Default priority
                acceptance_criteria=[f"Implements: {req_text[:50]}..."]
            ))
        return functional_reqs

    def _convert_non_functional_requirements(
        self,
        nfr_data: Dict[str, Any]
    ) -> List[NonFunctionalRequirement]:
        """
        Convert non-functional requirements from LLM output

        WHY: NFRs have multiple categories (performance, security, etc.)
        RESPONSIBILITY: Create NFR objects from categorized data
        """
        non_functional_reqs = []
        nfr_idx = 1

        # Performance requirements
        if "performance" in nfr_data:
            nfr_idx = self._add_performance_requirements(
                nfr_data["performance"],
                non_functional_reqs,
                nfr_idx
            )

        # Security requirements
        for security_req in nfr_data.get("security", []):
            non_functional_reqs.append(NonFunctionalRequirement(
                id=f"REQ-NF-{nfr_idx:03d}",
                title=security_req[:100],
                description=security_req,
                type=RequirementType.SECURITY,
                priority=Priority.CRITICAL
            ))
            nfr_idx += 1

        return non_functional_reqs

    def _convert_actors_to_stakeholders(
        self,
        llm_output: Dict[str, Any]
    ) -> List[Stakeholder]:
        """
        Convert actors to stakeholders

        WHY: LLM outputs "actors", domain model uses "stakeholders"
        RESPONSIBILITY: Semantic mapping between concepts
        """
        stakeholders = []
        for actor in llm_output.get("actors", []):
            stakeholders.append(Stakeholder(
                name=actor.get("name", "Unknown"),
                role=", ".join(actor.get("roles", [])),
                concerns=[f"Auth: {', '.join(actor.get('auth', []))}"]
            ))
        return stakeholders

    def _convert_risks_to_constraints(
        self,
        llm_output: Dict[str, Any]
    ) -> List[Constraint]:
        """
        Convert risks to constraints

        WHY: Risks are often constraints in disguise
        RESPONSIBILITY: Map risk concept to constraint model
        """
        constraints = []
        for risk in llm_output.get("risks", []):
            constraints.append(Constraint(
                type="risk",
                description=risk.get("item", ""),
                impact=risk.get("impact", "M"),
                mitigation=risk.get("mitigation")
            ))
        return constraints

    def _convert_assumptions(
        self,
        llm_output: Dict[str, Any]
    ) -> List[Assumption]:
        """
        Convert assumptions from LLM output

        WHY: Simple list to rich objects
        RESPONSIBILITY: Create Assumption objects
        """
        return [
            Assumption(description=assumption, risk_if_false="Unknown")
            for assumption in llm_output.get("assumptions", [])
        ]

    def _add_performance_requirements(
        self,
        perf_data: Dict[str, Any],
        non_functional_reqs: List[NonFunctionalRequirement],
        nfr_idx: int
    ) -> int:
        """
        Add performance requirements

        WHY: Performance data needs special handling
        RESPONSIBILITY: Convert performance metrics to NFRs

        Returns:
            Updated NFR index
        """
        if "p95_latency_ms" not in perf_data:
            return nfr_idx

        non_functional_reqs.append(NonFunctionalRequirement(
            id=f"REQ-NF-{nfr_idx:03d}",
            title=f"P95 Latency < {perf_data['p95_latency_ms']}ms",
            description=f"95th percentile latency must be under {perf_data['p95_latency_ms']} milliseconds",
            type=RequirementType.PERFORMANCE,
            priority=Priority.HIGH,
            metric="p95_latency_ms",
            target=f"< {perf_data['p95_latency_ms']}ms"
        ))
        return nfr_idx + 1

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(f"[RequirementsConverter] {message}")
